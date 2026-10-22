/*
 * clocklib: a tiny native library for the clock project.
 *
 * Python without imports cannot open a window, read the system time, wait or
 * beep, so this extension module provides exactly that and nothing else:
 *
 *   Window(title, width, height)   a Win32 window with a drawing surface
 *   sin(radians), cos(radians)     trigonometry
 *   system_time() -> (h, m, s)     local time of the machine
 *   ticks_ms()                     milliseconds since boot
 *   sleep(ms), beep()
 */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <windows.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

#define QUEUE_SIZE 256
#define CLASS_NAME L"ClockLibWindow"

typedef struct {
    PyObject_HEAD
    HWND hwnd;
    HDC memdc;
    HBITMAP bitmap;
    HGDIOBJ previous_bitmap;
    void *bits;
    int width;
    int height;
    int open;
    int queue[QUEUE_SIZE];
    int head;
    int count;
} WindowObject;

static int class_registered = 0;

static void push_char(WindowObject *self, int code)
{
    if (self->count < QUEUE_SIZE) {
        self->queue[(self->head + self->count) % QUEUE_SIZE] = code;
        self->count++;
    }
}

static void blit(WindowObject *self, HDC target)
{
    if (self->memdc != NULL) {
        BitBlt(target, 0, 0, self->width, self->height, self->memdc, 0, 0, SRCCOPY);
    }
}

static LRESULT CALLBACK window_proc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    WindowObject *self = (WindowObject *)GetWindowLongPtrW(hwnd, GWLP_USERDATA);

    if (msg == WM_NCCREATE) {
        CREATESTRUCTW *create = (CREATESTRUCTW *)lparam;
        SetWindowLongPtrW(hwnd, GWLP_USERDATA, (LONG_PTR)create->lpCreateParams);
    } else if (self != NULL) {
        switch (msg) {
        case WM_CHAR:
            push_char(self, (int)wparam);
            return 0;
        case WM_PAINT: {
            PAINTSTRUCT paint;
            HDC hdc = BeginPaint(hwnd, &paint);
            blit(self, hdc);
            EndPaint(hwnd, &paint);
            return 0;
        }
        case WM_ERASEBKGND:
            return 1;
        case WM_CLOSE:
            self->open = 0;
            DestroyWindow(hwnd);
            return 0;
        case WM_DESTROY:
            self->hwnd = NULL;
            self->open = 0;
            return 0;
        }
    }
    return DefWindowProcW(hwnd, msg, wparam, lparam);
}

static COLORREF to_colorref(int r, int g, int b)
{
    return RGB(r & 255, g & 255, b & 255);
}

/* ---------- Window lifecycle ---------- */

static PyObject *Window_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PyObject *title;
    int width, height;
    if (!PyArg_ParseTuple(args, "Uii", &title, &width, &height)) {
        return NULL;
    }
    if (width <= 0 || height <= 0) {
        PyErr_SetString(PyExc_ValueError, "Window dimensions must be positive");
        return NULL;
    }

    HINSTANCE instance = GetModuleHandleW(NULL);
    if (!class_registered) {
        WNDCLASSW wc;
        memset(&wc, 0, sizeof wc);
        wc.lpfnWndProc = window_proc;
        wc.hInstance = instance;
        wc.hCursor = LoadCursorW(NULL, MAKEINTRESOURCEW(32512));
        wc.lpszClassName = CLASS_NAME;
        if (!RegisterClassW(&wc)) {
            PyErr_SetString(PyExc_OSError, "Could not register the window class");
            return NULL;
        }
        class_registered = 1;
    }

    wchar_t *wide_title = PyUnicode_AsWideCharString(title, NULL);
    if (wide_title == NULL) {
        return NULL;
    }
    WindowObject *self = (WindowObject *)type->tp_alloc(type, 0);
    if (self == NULL) {
        PyMem_Free(wide_title);
        return NULL;
    }
    self->width = width;
    self->height = height;

    DWORD style = WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX;
    RECT rect = {0, 0, width, height};
    AdjustWindowRect(&rect, style, FALSE);

    self->hwnd = CreateWindowExW(0, CLASS_NAME, wide_title, style, CW_USEDEFAULT, CW_USEDEFAULT,
                                 rect.right - rect.left, rect.bottom - rect.top,
                                 NULL, NULL, instance, self);
    PyMem_Free(wide_title);
    if (self->hwnd == NULL) {
        Py_DECREF(self);
        PyErr_SetString(PyExc_OSError, "Could not create the window");
        return NULL;
    }

    BITMAPINFO info;
    memset(&info, 0, sizeof info);
    info.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    info.bmiHeader.biWidth = width;
    info.bmiHeader.biHeight = -height; /* top-down */
    info.bmiHeader.biPlanes = 1;
    info.bmiHeader.biBitCount = 32;
    info.bmiHeader.biCompression = BI_RGB;

    HDC screen = GetDC(self->hwnd);
    self->memdc = CreateCompatibleDC(screen);
    self->bitmap = CreateDIBSection(screen, &info, DIB_RGB_COLORS, &self->bits, NULL, 0);
    ReleaseDC(self->hwnd, screen);
    self->previous_bitmap = SelectObject(self->memdc, self->bitmap);
    SetBkMode(self->memdc, TRANSPARENT);

    self->open = 1;
    ShowWindow(self->hwnd, SW_SHOW);
    UpdateWindow(self->hwnd);
    return (PyObject *)self;
}

static void release_surface(WindowObject *self)
{
    if (self->memdc != NULL) {
        SelectObject(self->memdc, self->previous_bitmap);
        DeleteObject(self->bitmap);
        DeleteDC(self->memdc);
        self->memdc = NULL;
        self->bitmap = NULL;
    }
}

static void Window_dealloc(WindowObject *self)
{
    if (self->hwnd != NULL) {
        SetWindowLongPtrW(self->hwnd, GWLP_USERDATA, 0);
        DestroyWindow(self->hwnd);
    }
    release_surface(self);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *Window_close(WindowObject *self, PyObject *Py_UNUSED(ignored))
{
    if (self->hwnd != NULL) {
        DestroyWindow(self->hwnd);
    }
    self->open = 0;
    Py_RETURN_NONE;
}

static PyObject *Window_is_open(WindowObject *self, PyObject *Py_UNUSED(ignored))
{
    return PyBool_FromLong(self->open);
}

static PyObject *Window_poll(WindowObject *self, PyObject *Py_UNUSED(ignored))
{
    MSG msg;
    while (PeekMessageW(&msg, NULL, 0, 0, PM_REMOVE)) {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }
    PyObject *list = PyList_New(0);
    if (list == NULL) {
        return NULL;
    }
    while (self->count > 0) {
        PyObject *code = PyLong_FromLong(self->queue[self->head]);
        self->head = (self->head + 1) % QUEUE_SIZE;
        self->count--;
        if (code == NULL || PyList_Append(list, code) < 0) {
            Py_XDECREF(code);
            Py_DECREF(list);
            return NULL;
        }
        Py_DECREF(code);
    }
    return list;
}

static int require_surface(WindowObject *self)
{
    if (self->memdc == NULL || self->hwnd == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "The window is closed");
        return 0;
    }
    return 1;
}

/* ---------- Drawing ---------- */

static PyObject *Window_fill(WindowObject *self, PyObject *args)
{
    int r, g, b;
    if (!PyArg_ParseTuple(args, "(iii)", &r, &g, &b) || !require_surface(self)) {
        return NULL;
    }
    HBRUSH brush = CreateSolidBrush(to_colorref(r, g, b));
    RECT rect = {0, 0, self->width, self->height};
    FillRect(self->memdc, &rect, brush);
    DeleteObject(brush);
    Py_RETURN_NONE;
}

static HPEN make_pen(int thickness, COLORREF color)
{
    LOGBRUSH brush = {BS_SOLID, color, 0};
    return ExtCreatePen(PS_GEOMETRIC | PS_SOLID | PS_ENDCAP_ROUND | PS_JOIN_ROUND,
                        thickness < 1 ? 1 : thickness, &brush, 0, NULL);
}

static PyObject *Window_line(WindowObject *self, PyObject *args)
{
    int x1, y1, x2, y2, r, g, b, thickness;
    if (!PyArg_ParseTuple(args, "iiii(iii)i", &x1, &y1, &x2, &y2, &r, &g, &b, &thickness)
        || !require_surface(self)) {
        return NULL;
    }
    COLORREF color = to_colorref(r, g, b);
    HPEN pen = make_pen(thickness, color);
    HGDIOBJ old = SelectObject(self->memdc, pen);
    MoveToEx(self->memdc, x1, y1, NULL);
    LineTo(self->memdc, x2, y2);
    SetPixelV(self->memdc, x2, y2, color); /* LineTo leaves the last pixel out */
    SelectObject(self->memdc, old);
    DeleteObject(pen);
    Py_RETURN_NONE;
}

static PyObject *draw_ellipse(WindowObject *self, PyObject *args, int filled)
{
    int cx, cy, radius, r, g, b, thickness = 1;
    if (!PyArg_ParseTuple(args, "iii(iii)|i", &cx, &cy, &radius, &r, &g, &b, &thickness)
        || !require_surface(self)) {
        return NULL;
    }
    COLORREF color = to_colorref(r, g, b);
    HPEN pen = make_pen(filled ? 1 : thickness, color);
    HBRUSH brush = filled ? CreateSolidBrush(color) : (HBRUSH)GetStockObject(NULL_BRUSH);
    HGDIOBJ old_pen = SelectObject(self->memdc, pen);
    HGDIOBJ old_brush = SelectObject(self->memdc, brush);
    Ellipse(self->memdc, cx - radius, cy - radius, cx + radius + 1, cy + radius + 1);
    SelectObject(self->memdc, old_pen);
    SelectObject(self->memdc, old_brush);
    DeleteObject(pen);
    if (filled) {
        DeleteObject(brush);
    }
    Py_RETURN_NONE;
}

static PyObject *Window_circle(WindowObject *self, PyObject *args)
{
    return draw_ellipse(self, args, 0);
}

static PyObject *Window_fill_circle(WindowObject *self, PyObject *args)
{
    return draw_ellipse(self, args, 1);
}

static PyObject *Window_rect(WindowObject *self, PyObject *args)
{
    int x, y, w, h, r, g, b, thickness = 1, filled = 0;
    if (!PyArg_ParseTuple(args, "iiii(iii)|ip", &x, &y, &w, &h, &r, &g, &b, &thickness, &filled)
        || !require_surface(self)) {
        return NULL;
    }
    HBRUSH brush = CreateSolidBrush(to_colorref(r, g, b));
    if (filled) {
        RECT area = {x, y, x + w, y + h};
        FillRect(self->memdc, &area, brush);
    } else {
        RECT sides[4] = {
            {x, y, x + w, y + thickness},
            {x, y + h - thickness, x + w, y + h},
            {x, y, x + thickness, y + h},
            {x + w - thickness, y, x + w, y + h},
        };
        for (int i = 0; i < 4; i++) {
            FillRect(self->memdc, &sides[i], brush);
        }
    }
    DeleteObject(brush);
    Py_RETURN_NONE;
}

/* text(x, y, string, color, size, align=0, bold=False, mono=False)
 * align: 0 left, 1 centered, 2 right. y is the vertical middle of the text. */
static PyObject *Window_text(WindowObject *self, PyObject *args)
{
    int x, y, r, g, b, size, align = 0, bold = 0, mono = 0;
    PyObject *string;
    if (!PyArg_ParseTuple(args, "iiU(iii)i|ipp", &x, &y, &string, &r, &g, &b, &size,
                          &align, &bold, &mono)
        || !require_surface(self)) {
        return NULL;
    }
    Py_ssize_t length;
    wchar_t *text = PyUnicode_AsWideCharString(string, &length);
    if (text == NULL) {
        return NULL;
    }
    HFONT font = CreateFontW(-size, 0, 0, 0, bold ? FW_BOLD : FW_NORMAL, FALSE, FALSE, FALSE,
                             DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
                             CLEARTYPE_QUALITY, DEFAULT_PITCH | FF_DONTCARE,
                             mono ? L"Consolas" : L"Segoe UI");
    HGDIOBJ old = SelectObject(self->memdc, font);
    SetTextColor(self->memdc, to_colorref(r, g, b));
    UINT horizontal = align == 1 ? TA_CENTER : (align == 2 ? TA_RIGHT : TA_LEFT);
    SetTextAlign(self->memdc, horizontal | TA_TOP);
    SIZE extent;
    GetTextExtentPoint32W(self->memdc, text, (int)length, &extent);
    TextOutW(self->memdc, x, y - extent.cy / 2, text, (int)length);
    SelectObject(self->memdc, old);
    DeleteObject(font);
    PyMem_Free(text);
    Py_RETURN_NONE;
}

static PyObject *Window_present(WindowObject *self, PyObject *Py_UNUSED(ignored))
{
    if (self->hwnd != NULL) {
        HDC hdc = GetDC(self->hwnd);
        blit(self, hdc);
        ReleaseDC(self->hwnd, hdc);
    }
    Py_RETURN_NONE;
}

static PyObject *Window_save_bmp(WindowObject *self, PyObject *args)
{
    const char *path;
    if (!PyArg_ParseTuple(args, "s", &path) || !require_surface(self)) {
        return NULL;
    }
    BITMAPFILEHEADER file_header;
    BITMAPINFOHEADER info_header;
    DWORD row_bytes = (DWORD)self->width * 4;
    DWORD image_size = row_bytes * (DWORD)self->height;
    memset(&file_header, 0, sizeof file_header);
    memset(&info_header, 0, sizeof info_header);
    file_header.bfType = 0x4D42;
    file_header.bfOffBits = sizeof file_header + sizeof info_header;
    file_header.bfSize = file_header.bfOffBits + image_size;
    info_header.biSize = sizeof info_header;
    info_header.biWidth = self->width;
    info_header.biHeight = self->height; /* bottom-up */
    info_header.biPlanes = 1;
    info_header.biBitCount = 32;
    info_header.biCompression = BI_RGB;
    info_header.biSizeImage = image_size;

    FILE *file = fopen(path, "wb");
    if (file == NULL) {
        return PyErr_SetFromErrnoWithFilename(PyExc_OSError, path);
    }
    fwrite(&file_header, sizeof file_header, 1, file);
    fwrite(&info_header, sizeof info_header, 1, file);
    for (int row = self->height - 1; row >= 0; row--) {
        fwrite((char *)self->bits + (size_t)row * row_bytes, 1, row_bytes, file);
    }
    fclose(file);
    Py_RETURN_NONE;
}

static PyMethodDef Window_methods[] = {
    {"close", (PyCFunction)Window_close, METH_NOARGS, "Close the window."},
    {"is_open", (PyCFunction)Window_is_open, METH_NOARGS, "True while the window exists."},
    {"poll", (PyCFunction)Window_poll, METH_NOARGS,
     "Process window events. Returns the character codes typed since the last call."},
    {"fill", (PyCFunction)Window_fill, METH_VARARGS, "fill((r, g, b))"},
    {"line", (PyCFunction)Window_line, METH_VARARGS, "line(x1, y1, x2, y2, (r, g, b), thickness)"},
    {"circle", (PyCFunction)Window_circle, METH_VARARGS, "circle(cx, cy, radius, (r, g, b), thickness=1)"},
    {"fill_circle", (PyCFunction)Window_fill_circle, METH_VARARGS, "fill_circle(cx, cy, radius, (r, g, b))"},
    {"rect", (PyCFunction)Window_rect, METH_VARARGS, "rect(x, y, w, h, (r, g, b), thickness=1, filled=False)"},
    {"text", (PyCFunction)Window_text, METH_VARARGS,
     "text(x, y, string, (r, g, b), size, align=0, bold=False, mono=False)"},
    {"present", (PyCFunction)Window_present, METH_NOARGS, "Show what was drawn."},
    {"save_bmp", (PyCFunction)Window_save_bmp, METH_VARARGS, "save_bmp(path)"},
    {NULL, NULL, 0, NULL}
};

static PyTypeObject WindowType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "clocklib.Window",
    .tp_basicsize = sizeof(WindowObject),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = "A native window with a drawing surface.",
    .tp_new = Window_new,
    .tp_dealloc = (destructor)Window_dealloc,
    .tp_methods = Window_methods,
};

/* ---------- Module functions ---------- */

static PyObject *clocklib_sin(PyObject *self, PyObject *args)
{
    double angle;
    if (!PyArg_ParseTuple(args, "d", &angle)) {
        return NULL;
    }
    return PyFloat_FromDouble(sin(angle));
}

static PyObject *clocklib_cos(PyObject *self, PyObject *args)
{
    double angle;
    if (!PyArg_ParseTuple(args, "d", &angle)) {
        return NULL;
    }
    return PyFloat_FromDouble(cos(angle));
}

static PyObject *clocklib_system_time(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    SYSTEMTIME now;
    GetLocalTime(&now);
    return Py_BuildValue("(iii)", now.wHour, now.wMinute, now.wSecond);
}

static PyObject *clocklib_ticks_ms(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    return PyLong_FromUnsignedLongLong(GetTickCount64());
}

static PyObject *clocklib_sleep(PyObject *self, PyObject *args)
{
    unsigned long milliseconds;
    if (!PyArg_ParseTuple(args, "k", &milliseconds)) {
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    Sleep((DWORD)milliseconds);
    Py_END_ALLOW_THREADS
    Py_RETURN_NONE;
}

static PyObject *clocklib_beep(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    MessageBeep(MB_ICONEXCLAMATION);
    Py_RETURN_NONE;
}

static PyMethodDef module_methods[] = {
    {"sin", clocklib_sin, METH_VARARGS, "Sine of an angle in radians."},
    {"cos", clocklib_cos, METH_VARARGS, "Cosine of an angle in radians."},
    {"system_time", clocklib_system_time, METH_NOARGS, "Local (hours, minutes, seconds)."},
    {"ticks_ms", clocklib_ticks_ms, METH_NOARGS, "Milliseconds since the system started."},
    {"sleep", clocklib_sleep, METH_VARARGS, "sleep(milliseconds)"},
    {"beep", clocklib_beep, METH_NOARGS, "Play the system alert sound."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module_definition = {
    PyModuleDef_HEAD_INIT, "clocklib", "Native window, time and sound for the clock.", -1,
    module_methods
};

PyMODINIT_FUNC PyInit_clocklib(void)
{
    if (PyType_Ready(&WindowType) < 0) {
        return NULL;
    }
    PyObject *module = PyModule_Create(&module_definition);
    if (module == NULL) {
        return NULL;
    }
    Py_INCREF(&WindowType);
    if (PyModule_AddObject(module, "Window", (PyObject *)&WindowType) < 0) {
        Py_DECREF(&WindowType);
        Py_DECREF(module);
        return NULL;
    }
    return module;
}

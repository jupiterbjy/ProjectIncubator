
// OpenGLStreamDemoDlg.cpp: 구현 파일
//

#include "pch.h"
#include "framework.h"
#include "OpenGLStreamDemo.h"
#include "OpenGLStreamDemoDlg.h"
#include "afxdialogex.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif
#pragma comment(linker, "/entry:WinMainCRTStartup /subsystem:console")

// COpenGLStreamDemoDlg 대화 상자


COpenGLStreamDemoDlg::COpenGLStreamDemoDlg(CWnd* pParent /*=nullptr*/)
	: CDialogEx(IDD_OPENGLSTREAMDEMO_DIALOG, pParent)
{
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void COpenGLStreamDemoDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
	// DDX_Control(pDX, IDC_PICTURE_CTL, m_picture);
}

BEGIN_MESSAGE_MAP(COpenGLStreamDemoDlg, CDialogEx)
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_WM_CREATE()
	ON_WM_DESTROY()
	ON_WM_TIMER()
END_MESSAGE_MAP()


// COpenGLStreamDemoDlg 메시지 처리기

BOOL COpenGLStreamDemoDlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();

	// 이 대화 상자의 아이콘을 설정합니다.  응용 프로그램의 주 창이 대화 상자가 아닐 경우에는
	//  프레임워크가 이 작업을 자동으로 수행합니다.
	SetIcon(m_hIcon, TRUE);			// 큰 아이콘을 설정합니다.
	SetIcon(m_hIcon, FALSE);		// 작은 아이콘을 설정합니다.

	// TODO: 여기에 추가 초기화 작업을 추가합니다.
	// TODO: 여기에 생성 코드를 추가합니다.
	hMapFile = OpenFileMapping(
		FILE_MAP_ALL_ACCESS, FALSE, TEXT("MAPPING_OBJECT")
	);

	if (hMapFile == NULL) {
		std::string msg = "OpenFileMapping failed with: " + std::to_string(GetLastError());
		MessageBox(CString(msg.c_str()));
		return FALSE;
	}

	// TODO: change temp size or use default value at start of communication
	size_t buff_size = 800 * 600 * 4;

	pBuf = (unsigned char*)MapViewOfFile(
		hMapFile, FILE_MAP_ALL_ACCESS, 0, 0, buff_size
	);

	if (pBuf == NULL) {
		std::string msg = "MapViewOfFile failed with: " + std::to_string(GetLastError());
		MessageBox(CString(msg.c_str()));
		CloseHandle(hMapFile);
		return FALSE;
	}

	//// Gen & bind tex
	//glGenTextures(1, &texture_id);
	//glBindTexture(GL_TEXTURE_2D, texture_id);

	//// Set tex params
	//glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
	//glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
	//// glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
	//// glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);

	//// Set initial tex data with null data
	//glTexImage2D(
	//	GL_TEXTURE_2D, 0, GL_RGBA, 800, 600, 0, GL_RGBA, GL_UNSIGNED_BYTE, NULL
	//);

	return TRUE;  // 포커스를 컨트롤에 설정하지 않으면 TRUE를 반환합니다.
}

// 대화 상자에 최소화 단추를 추가할 경우 아이콘을 그리려면
//  아래 코드가 필요합니다.  문서/뷰 모델을 사용하는 MFC 애플리케이션의 경우에는
//  프레임워크에서 이 작업을 자동으로 수행합니다.

void COpenGLStreamDemoDlg::OnPaint()
{
	if (IsIconic())
	{
		CPaintDC dc(this); // 그리기를 위한 디바이스 컨텍스트입니다.

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// 클라이언트 사각형에서 아이콘을 가운데에 맞춥니다.
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// 아이콘을 그립니다.
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDC* current_dc = GetDC();
		//CDC memDC;
		//memDC.CreateCompatibleDC(current_dc);

		//CImage image;
		//image.Create(800, 600, 32);

		//void* p_bits = image.GetBits();
		//int pitch = image.GetPitch();

		//for (int i = 0; i < 800; i++)
		//	printf("%d\n", (unsigned int)pBuf[i]);

		//printf("\n");

		SetDIBitsToDevice(
			current_dc->m_hDC,
			0, 0, 800, 600,
			0, 0, 0, 600,
			pBuf, m_bmi, DIB_RGB_COLORS
		);

		// EndPaint(current_dc->m_hDC);
		ReleaseDC(current_dc);

		// CDialogEx::OnPaint();
	}
}

// 사용자가 최소화된 창을 끄는 동안에 커서가 표시되도록 시스템에서
//  이 함수를 호출합니다.
HCURSOR COpenGLStreamDemoDlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}



BOOL COpenGLStreamDemoDlg::GetRenderingConext()
{
	MessageBox(CString("Error setting up OpenGL"));
	return -1;
}

int COpenGLStreamDemoDlg::OnCreate(LPCREATESTRUCT lpCreateStruct)
{
	if (CDialogEx::OnCreate(lpCreateStruct) == -1)
		return -1;

	// TODO:  여기에 특수화된 작성 코드를 추가합니다.

	// glBindTexture(GL_TEXTURE_2D, texture_id);
	// glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, 1920, 1080, GL_RGBA, GL_UNSIGNED_BYTE, pBuf);

	// https://blog.naver.com/onlyjeje/30181239359

	m_bmi = (BITMAPINFO*)malloc(sizeof(BITMAPINFO) + 256 * sizeof(RGBQUAD));

	m_bmi->bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
	m_bmi->bmiHeader.biWidth = 800;
	m_bmi->bmiHeader.biHeight = 600;
	m_bmi->bmiHeader.biPlanes = 1;
	m_bmi->bmiHeader.biBitCount = 32;
	m_bmi->bmiHeader.biCompression = 0;
	m_bmi->bmiHeader.biSizeImage = 800 * 600 * 4;

	m_bmi->bmiHeader.biXPelsPerMeter = 0;
	m_bmi->bmiHeader.biYPelsPerMeter = 0;
	m_bmi->bmiHeader.biClrUsed = 256;
	m_bmi->bmiHeader.biClrImportant = 256;

	for (size_t idx = 0; idx < 256; idx++) {
		m_bmi->bmiColors[idx].rgbBlue = idx;
		m_bmi->bmiColors[idx].rgbGreen = idx;
		m_bmi->bmiColors[idx].rgbRed = idx;
		m_bmi->bmiColors[idx].rgbReserved = 0;
	}

	SetTimer(1000, 1000, NULL);

	return 0;
}


void COpenGLStreamDemoDlg::OnDestroy()
{
	CDialogEx::OnDestroy();

	// TODO: 여기에 메시지 처리기 코드를 추가합니다.
	if (FALSE == ::wglDeleteContext(m_hrc))
	{
		MessageBox(CString("Error deleting rendering context"));
	}
}


void COpenGLStreamDemoDlg::OnTimer(UINT_PTR nIDEvent)
{
	
	Invalidate();
	//OnPaint();
	// SwapBuffers(m_pDC->GetSafeHdc());
	CDialogEx::OnTimer(nIDEvent);
}

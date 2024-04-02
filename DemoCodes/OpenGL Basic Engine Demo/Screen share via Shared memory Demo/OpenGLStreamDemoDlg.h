
// OpenGLStreamDemoDlg.h: 헤더 파일
//

#pragma once

#include <string>
#include <Windows.h>
#include <GL/glew.h>


// COpenGLStreamDemoDlg 대화 상자
class COpenGLStreamDemoDlg : public CDialogEx
{
// 생성입니다.
public:
	COpenGLStreamDemoDlg(CWnd* pParent = nullptr);	// 표준 생성자입니다.

// 대화 상자 데이터입니다.
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_OPENGLSTREAMDEMO_DIALOG };
#endif

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV 지원입니다.


// 구현입니다.
protected:
	HICON m_hIcon;

	// 생성된 메시지 맵 함수
	virtual BOOL OnInitDialog();
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	DECLARE_MESSAGE_MAP()

	// shared memory
	HANDLE hMapFile = nullptr;
	unsigned char* pBuf = nullptr;
	GLuint texture_id = 0;

	// OpenGL setup
	BOOL GetRenderingConext();
	HGLRC m_hrc;
	CDC* m_pDC;
	BITMAPINFO* m_bmi;

public:
	// CStatic m_picture;
	afx_msg int OnCreate(LPCREATESTRUCT lpCreateStruct);
	afx_msg void OnDestroy();
	afx_msg void OnTimer(UINT_PTR nIDEvent);
};

# GitHub Pages 배포 가이드

이 가이드는 macOS Kext Visualization 프로젝트를 GitHub Pages에 배포하는 방법을 설명합니다.

## 방법 1: GitHub Actions 사용 (권장)

### 1단계: 저장소 초기화

```bash
# 빈 저장소 클론
cd /Users/gap_dev/bob_proj/metal
mkdir MacOS-kext-visualization
cd MacOS-kext-visualization
git init
git remote add origin https://github.com/Apple-Reversing-Tools/MacOS-kext-visualization.git
```

### 2단계: 파일 복사 및 푸시

```bash
# deploy 폴더의 모든 내용을 현재 디렉토리로 복사
cp -r deploy/* .

# GitHub Actions 워크플로우 파일 복사
cp -r deploy/.github ./

# 커밋 및 푸시
git add .
git commit -m "Initial commit: Add kext visualization files"
git branch -M main
git push -u origin main
```

### 3단계: GitHub Pages 활성화

1. GitHub에서 저장소 페이지로 이동
2. **Settings** > **Pages** 클릭
3. **Source** 섹션에서 "GitHub Actions" 선택
4. 저장 후 자동으로 배포 시작됨

### 4단계: 접근

약 1-2분 후 다음 URL에서 확인 가능:
```
https://Apple-Reversing-Tools.github.io/MacOS-kext-visualization/
```

---

## 방법 2: gh-pages 브랜치 사용

### 1단계: 저장소 초기화

```bash
cd /Users/gap_dev/bob_proj/metal
mkdir MacOS-kext-visualization
cd MacOS-kext-visualization
git init
git remote add origin https://github.com/Apple-Reversing-Tools/MacOS-kext-visualization.git
```

### 2단계: main 브랜치에 파이썬 소스 파일만 커밋

```bash
# README와 소스 파일만 추가
git add ../analyze_kext_only.py ../analyze_kext_plist.py ../compare_kexts.py
cp ../README.md ./
cp -r deploy/* ./
git add README.md
git commit -m "Add source files"
git branch -M main
git push -u origin main
```

### 3단계: gh-pages 브랜치 생성 및 배포

```bash
# gh-pages 브랜치 생성
git checkout --orphan gh-pages
git rm -rf .

# deploy 폴더의 모든 파일 복사
cp -r ../deploy/* .

# 정적 파일만 추가 (index.html, kext_visualization.html 등)
git add index.html README.md
git add vmapple_kext/ host_kext/
git commit -m "Deploy to GitHub Pages"

# gh-pages 브랜치 푸시
git push -u origin gh-pages

# main 브랜치로 돌아가기
git checkout main
```

### 4단계: GitHub Pages 설정

1. GitHub에서 저장소 페이지로 이동
2. **Settings** > **Pages** 클릭
3. **Source** 섹션에서 "Deploy from a branch" 선택
4. Branch를 "gh-pages"로 선택
5. Save 클릭

---

## 빠른 배포 (한 번에)

```bash
# 전체 배포 스크립트
cd /Users/gap_dev/bob_proj/metal
git clone https://github.com/Apple-Reversing-Tools/MacOS-kext-visualization.git temp_repo
cd temp_repo

# 파일 복사
cp -r ../deploy/* .
cp -r ../deploy/.github .

# 커밋 및 푸시
git add .
git commit -m "Initial deployment"
git push origin main

cd ..
rm -rf temp_repo
```

이후 GitHub 저장소의 Settings > Pages에서 "GitHub Actions"를 선택하면 자동 배포됩니다.

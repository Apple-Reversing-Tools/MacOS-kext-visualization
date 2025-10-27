#!/bin/bash

# GitHub Pages 배포 스크립트
# 사용법: ./deploy_to_github.sh

set -e  # 에러 발생 시 중단

echo "========================================="
echo "GitHub Pages 배포 시작"
echo "========================================="

# 저장소 URL
REPO_URL="https://github.com/Apple-Reversing-Tools/MacOS-kext-visualization.git"
REPO_NAME="MacOS-kext-visualization"

# 현재 위치 확인
CURRENT_DIR=$(pwd)
DEPLOY_DIR="$CURRENT_DIR"
PARENT_DIR=$(dirname "$CURRENT_DIR")

echo "현재 디렉토리: $CURRENT_DIR"

# 배포용 임시 디렉토리
TEMP_DIR="$PARENT_DIR/temp_repo"

# 임시 디렉토리가 있으면 삭제
if [ -d "$TEMP_DIR" ]; then
    echo "기존 임시 디렉토리 삭제 중..."
    rm -rf "$TEMP_DIR"
fi

# 저장소 클론
echo "저장소 클론 중..."
git clone "$REPO_URL" "$TEMP_DIR"
cd "$TEMP_DIR"

# 기본 브랜치를 main으로 설정
git checkout -b main 2>/dev/null || git checkout main

# deploy 폴더의 모든 파일 복사
echo "파일 복사 중..."
cp -r "$DEPLOY_DIR"/* .
cp -r "$DEPLOY_DIR"/.github . 2>/dev/null || true

# .git 폴더가 복사되지 않도록 확인
rm -rf .git
git init
git remote add origin "$REPO_URL"

# 모든 파일 추가
git add .

# 커밋
echo "커밋 중..."
git commit -m "Deploy to GitHub Pages: $(date '+%Y-%m-%d %H:%M:%S')" || echo "변경사항 없음"

# main 브랜치로 푸시
echo "푸시 중..."
git branch -M main
git push -u origin main --force

# 정리
echo "임시 파일 정리 중..."
cd "$PARENT_DIR"
rm -rf "$TEMP_DIR"

echo "========================================="
echo "배포 완료!"
echo "========================================="
echo ""
echo "다음 단계:"
echo "1. https://github.com/Apple-Reversing-Tools/MacOS-kext-visualization 로 이동"
echo "2. Settings > Pages 클릭"
echo "3. Source를 'GitHub Actions'로 선택"
echo "4. 약 1-2분 후 다음 URL에서 확인:"
echo "   https://Apple-Reversing-Tools.github.io/MacOS-kext-visualization/"
echo ""

# AI/SW 개발 워크스테이션 구축

## 1. 프로젝트 개요
터미널, Docker, Git을 활용한 재현 가능한 개발 환경 구축 미션

## 제출 안내

### 제출 방식
- 제출은 GitHub Repository 링크로 진행한다.
- 기술 문서(`README.md` 등)에 수행 로그와 증거를 모두 포함한다.
- 수행 로그/증거를 별도 파일로 분리할 수 있으나, `README.md`에서 링크로 접근 가능해야 한다.

### 실행 방식
- 모든 작업은 터미널(CLI) 기반으로 수행한다.
- `Dockerfile`은 직접 작성한다.
- 포트 매핑과 마운트/볼륨은 직접 설정하고 동작을 검증한다.

### 증거 수집 규칙
- 캡처/로그에는 반드시 `명령어 입력`과 `출력 결과`가 함께 포함되어야 한다.
- 브라우저 접속 증거에는 주소창(포트 포함)과 응답 화면이 함께 보여야 한다.
- 민감정보는 로그/이미지에 남기지 않으며, 노출 시 마스킹 처리한다.

### 재현성
- 평가자가 `README.md`만 보고 동일 절차를 따라 결과를 확인할 수 있어야 한다.
- 특정 개인 PC에 종속된 경로/설정이 있는 경우, 대체 방법 또는 주의사항을 함께 기록한다.

## 2. 실행 환경
| 항목 | 버전 |
|------|------|
| OS | macOS 15.x (Darwin 25.3.0) |
| Shell | zsh |
| Terminal | iTerm2 |
| Docker | 28.0.4 |
| Git | 저장소 초기화 상태(버전 출력 로그 미수집) |

## 3. 수행 체크리스트
- [x] 터미널 기본 조작 (pwd, ls, mkdir, cp, mv, rm, cat, touch)
- [x] 권한 실습 (chmod 644/755/700, 파일+디렉토리)
- [x] Docker 설치/점검 (version, info)
- [x] hello-world 실행
- [x] ubuntu 컨테이너 진입 + attach/exec 차이 정리
- [x] Dockerfile 커스텀 이미지 빌드
- [x] 포트 매핑 접속 (8080, 8081)
- [x] 바인드 마운트 변경 반영 확인
- [x] Docker 볼륨 영속성 검증
- [x] Git 설정 + GitHub 연동

## 4. 수행 로그

### 4.1 터미널 조작
```bash
$ pwd
/Users/jodonghyeon/Documents/codyssey

$ ls -la
drwxr-xr-x ... .git

$ mkdir test
$ cd test
$ touch hello.txt
$ echo "Hello World" > hello.txt
$ cat hello.txt
Hello World

$ cp hello.txt hello_backup.txt
$ mv hello_backup.txt renamed.txt
$ ll
-rw-r--r-- ... hello.txt
-rw-r--r-- ... renamed.txt

$ rm renamed.txt
$ mkdir sub
$ rmdir sub
```

### 4.2 권한 실습
```bash
$ touch perm_test.txt
$ ll
-rw-r--r-- ... perm_test.txt

$ chmod 755 perm_test.txt
$ ll
-rwxr-xr-x ... perm_test.txt

$ mkdir perm_dir
$ ll
drwxr-xr-x ... perm_dir

$ chmod 700 perm_dir
$ ll
drwx------ ... perm_dir
```

### 4.3 Docker 점검
```bash
$ docker --version
Docker version 28.0.4, build b8034c0

$ docker info
(Docker daemon 정상 응답 확인)
```

### 4.4 컨테이너 실행
```bash
$ docker run hello-world
Hello from Docker!
This message shows that your installation appears to be working correctly.

$ docker run -it --name ubuntu-test ubuntu:22.04 bash
root@...:/# ls
bin boot dev ...
root@...:/# echo "inside container"
inside container
root@...:/# exit

$ docker ps -a
... ubuntu-test ... Exited (0) ...

$ docker logs ubuntu-test
inside container
exit
```

### 4.5 Dockerfile 빌드 & 포트 매핑
```bash
$ docker build -t my-nginx:1.0 .
[+] Building ... FINISHED

$ docker run -d -p 8080:80 --name web-8080 my-nginx:1.0
$ docker run -d -p 8081:80 --name web-8081 my-nginx:1.0

$ curl http://localhost:8080
<!DOCTYPE html>
<h1>🚀 My Custom Nginx Server</h1>

$ curl http://localhost:8081
<!DOCTYPE html>
<h1>🚀 My Custom Nginx Server</h1>
```

**브라우저 접속 증거:**
아래 스크린샷 섹션에 첨부 (주소창 + 포트 + 응답 화면 포함)

### 4.6 바인드 마운트
```bash
$ docker run -d -p 8082:80 --name web-bind \
  -v $(pwd)/app:/usr/share/nginx/html:ro \
  nginx:alpine

$ curl http://localhost:8082
<h1>🔥 바인드 마운트 변경 반영!</h1>

$ cat > app/index.html << 'EOF'
... 수정 내용 반영 ...
EOF

$ curl http://localhost:8082
<!DOCTYPE html>
<h1>🔥 바인드 마운트 변경 반영!</h1>
```

### 4.7 볼륨 영속성
```bash
$ docker volume create mydata
mydata

$ docker run -d --name vol-test -v mydata:/data ubuntu:22.04 sleep infinity
$ docker exec vol-test bash -c "echo 'persistent data!' > /data/hello.txt && cat /data/hello.txt"
persistent data!

$ docker rm -f vol-test

$ docker run -d --name vol-test2 -v mydata:/data ubuntu:22.04 sleep infinity
$ docker exec vol-test2 bash -c "cat /data/hello.txt"
persistent data!

$ docker volume ls
... mydata
```

### 4.8 Git 설정
```bash
$ git config --list
(실행했으나 본문 로그 미기록)
```

### 4.9 정리/정지 작업
```bash
$ docker rm -f web-bind vol-test vol-test2
$ docker rm -f web-8080 web-8081
```
불필요한 실습 컨테이너 정리 후 상태 확인 완료.

## 5. 트러블슈팅

### 이슈 1: 컨테이너 attach 중 종료 제어
- **문제**: `docker attach bg-test` 이후 `SIGTERM/SIGINT` 메시지 출력
- **원인**: attach 세션에서 종료 시그널이 전달되며 제어가 꼬임
- **확인**: `got 3 SIGTERM/SIGINTs, forcefully exiting`
- **해결**: `docker rm -f bg-test`로 컨테이너 정리 후 `exec` 중심으로 재검증

### 이슈 2: 한글 깨짐 및 기존 컨테이너 충돌
- **문제**: 브라우저/터미널 확인 시 한글 출력이 깨지거나, 기존 `web-8080`, `web-8081` 컨테이너와 충돌 가능성 발생
- **원인**: 초기 HTML에 UTF-8 메타 태그 미포함 상태가 있었고, 동일 이름/포트의 기존 컨테이너가 남아 재실행 시 충돌 위험 존재
- **확인**: `curl http://localhost:8080`, `curl http://localhost:8081` 출력으로 한글 표시 상태 점검 및 `docker ps`로 컨테이너 상태 확인
- **해결**: `meta charset="UTF-8"` 포함 HTML 재생성 후, `docker rm -f web-8080 web-8081` → `docker build -t my-nginx:1.0 .` → `docker run -d -p 8080:80 --name web-8080 my-nginx:1.0` / `docker run -d -p 8081:80 --name web-8081 my-nginx:1.0` 순서로 재배포하여 정상 출력 확인

## 6. 검증 방법 요약
| 항목 | 검증 명령 | 결과 위치 |
|------|-----------|-----------|
| Docker 설치 | `docker --version` | 4.3절 |
| hello-world | `docker run hello-world` | 4.4절 |
| 포트 매핑 | `curl localhost:8080`, `curl localhost:8081` | 4.5절 + 스크린샷 |
| 바인드 마운트 | 호스트 파일 수정 → curl | 4.6절 |
| 볼륨 영속성 | 컨테이너 삭제 후 cat | 4.7절 |
| 컨테이너 로그 확인 | `docker logs ubuntu-test` | 4.4절 |

# 여기서 부터 스크린샷

![](./images/스크린샷%202026-04-01%20오후%206.54.54.png)
![](./images/스크린샷%202026-04-01%20오후%206.56.45.png)
![](./images/스크린샷%202026-04-01%20오후%206.58.18.png)
![](./images/스크린샷%202026-04-01%20오후%207.00.09.png)
![](./images/스크린샷%202026-04-01%20오후%207.02.52.png)
![](./images/스크린샷%202026-04-01%20오후%207.04.41.png)
![](./images/스크린샷%202026-04-01%20오후%207.05.15.png)
![](./images/스크린샷%202026-04-01%20오후%207.05.45.png)
![](./images/스크린샷%202026-04-01%20오후%207.06.33.png)
![](./images/스크린샷%202026-04-01%20오후%207.08.35.png)
![](./images/스크린샷%202026-04-01%20오후%207.08.51.png)
![](./images/스크린샷%202026-04-01%20오후%207.09.46.png)
![](./images/스크린샷%202026-04-01%20오후%207.11.01.png)
![](./images/스크린샷%202026-04-01%20오후%207.11.07.png)
![](./images/스크린샷%202026-04-01%20오후%207.12.40.png)

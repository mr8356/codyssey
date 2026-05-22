# 시스템 관제 자동화 스크립트 개발 - 수행 내역서

---

## 목차

1. [개발 환경](https://www.notion.so/360868381526803d8442d5bf84f11dd2?pvs=21)
2. [기본 보안 및 네트워크 설정](https://www.notion.so/360868381526803d8442d5bf84f11dd2?pvs=21)
3. [계정/그룹/권한 체계 구성](https://www.notion.so/360868381526803d8442d5bf84f11dd2?pvs=21)
4. [애플리케이션 실행 환경 구성](https://www.notion.so/360868381526803d8442d5bf84f11dd2?pvs=21)
5. [시스템 관제 자동화 스크립트 구현](https://www.notion.so/360868381526803d8442d5bf84f11dd2?pvs=21)
6. [자동 실행(cron) 설정](https://www.notion.so/360868381526803d8442d5bf84f11dd2?pvs=21)
7. [필수 증거 자료 체크리스트](https://www.notion.so/360868381526803d8442d5bf84f11dd2?pvs=21)

---

## 개발 환경


| 항목     | 내용               |
| ------ | ---------------- |
| OS     | Ubuntu 22.04 LTS |
| Shell  | Bash             |
| Python | 3.x (제공 앱 실행용)   |
| 실행 환경  | 컨테이너 / VM        |


---

## 1. 기본 보안 및 네트워크 설정

### 1-1. SSH 설정

### 수행 명령어

```bash
# sshd_config 파일 편집
sudo vi /etc/ssh/sshd_config

```

### 변경 내용 (`/etc/ssh/sshd_config`)

```
# 기존: #Port 22
Port 20022

# 기존: #PermitRootLogin prohibit-password
PermitRootLogin no

```

### SSH 서비스 재시작 및 확인

```bash
# sshd 재시작
sudo systemctl restart sshd

# 포트 리슨 상태 확인
ss -tulnp | grep sshd

```

### 확인 결과 (예시 출력)

```
tcp   LISTEN  0  128  0.0.0.0:20022  0.0.0.0:*  users:(("sshd",pid=XXXX,fd=3))
tcp   LISTEN  0  128     [::]:20022     [::]:*  users:(("sshd",pid=XXXX,fd=4))

```

> ✅ **확인 포인트**: 22번 포트가 아닌 **20022번 포트**로 sshd가 LISTEN 중인 것을 확인

---

### 1-2. 방화벽 설정 (UFW 선택)

### UFW 활성화 및 규칙 설정

```bash
# UFW 활성화
sudo ufw enable

# 기존 규칙 초기화 (선택)
sudo ufw --force reset

# 허용 포트 등록
sudo ufw allow 20022/tcp   # SSH
sudo ufw allow 15034/tcp   # APP

# 상태 확인
sudo ufw status verbose

```

### 확인 결과 (예시 출력)

```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)

To                         Action      From
--                         ------      ----
20022/tcp                  ALLOW IN    Anywhere
15034/tcp                  ALLOW IN    Anywhere
20022/tcp (v6)             ALLOW IN    Anywhere (v6)
15034/tcp (v6)             ALLOW IN    Anywhere (v6)

```

> ✅ **확인 포인트**: **20022/tcp**, **15034/tcp** 두 포트만 허용된 것을 확인

---

## 2. 계정/그룹/권한 체계 구성

### 2-1. 그룹 생성

```bash
# 그룹 생성
sudo groupadd agent-common
sudo groupadd agent-core

```

### 2-2. 계정 생성

```bash
# agent-admin 생성
sudo useradd -m -s /bin/bash agent-admin

# agent-dev 생성
sudo useradd -m -s /bin/bash agent-dev

# agent-test 생성
sudo useradd -m -s /bin/bash agent-test

# 비밀번호 설정 (각 계정별)
sudo passwd agent-admin
sudo passwd agent-dev
sudo passwd agent-test

```

### 2-3. 그룹 멤버 등록

```bash
# agent-common 그룹: admin, dev, test 모두 포함
sudo usermod -aG agent-common agent-admin
sudo usermod -aG agent-common agent-dev
sudo usermod -aG agent-common agent-test

# agent-core 그룹: admin, dev만 포함
sudo usermod -aG agent-core agent-admin
sudo usermod -aG agent-core agent-dev

```

### 2-4. 계정/그룹 확인

```bash
id agent-admin
id agent-dev
id agent-test

```

### 확인 결과 (예시 출력)

```
uid=1001(agent-admin) gid=1001(agent-admin) groups=1001(agent-admin),1002(agent-common),1003(agent-core)
uid=1002(agent-dev)   gid=1002(agent-dev)   groups=1002(agent-dev),1002(agent-common),1003(agent-core)
uid=1003(agent-test)  gid=1003(agent-test)  groups=1003(agent-test),1002(agent-common)

```

> ✅ **확인 포인트**: agent-test는 agent-core 그룹에 **포함되지 않음**

---

### 2-5. 디렉토리 구조 생성 및 권한 설정

### 환경 변수 사전 정의

```bash
export AGENT_HOME=/home/agent-admin/agent-app

```

### 디렉토리 생성

```bash
# AGENT_HOME 및 하위 디렉토리 생성
sudo mkdir -p $AGENT_HOME/upload_files
sudo mkdir -p $AGENT_HOME/api_keys
sudo mkdir -p $AGENT_HOME/bin
sudo mkdir -p /var/log/agent-app

```

### 소유자 및 권한 설정

```bash
# AGENT_HOME 전체 소유자 설정
sudo chown -R agent-admin:agent-core $AGENT_HOME

# upload_files: agent-common 그룹 R/W
sudo chown agent-admin:agent-common $AGENT_HOME/upload_files
sudo chmod 770 $AGENT_HOME/upload_files

# api_keys: agent-core 그룹 ONLY R/W
sudo chown agent-admin:agent-core $AGENT_HOME/api_keys
sudo chmod 770 $AGENT_HOME/api_keys
sudo chmod o-rwx $AGENT_HOME/api_keys   # 기타 사용자 접근 차단

# /var/log/agent-app: agent-core 그룹 ONLY R/W
sudo chown agent-admin:agent-core /var/log/agent-app
sudo chmod 770 /var/log/agent-app
sudo chmod o-rwx /var/log/agent-app     # 기타 사용자 접근 차단

```

### ACL 설정 (세밀한 권한 제어)

```bash
# acl 패키지 설치 (미설치 시)
sudo apt install -y acl

# upload_files: agent-common 그룹 rwx ACL 부여
sudo setfacl -m g:agent-common:rwx $AGENT_HOME/upload_files
sudo setfacl -d -m g:agent-common:rwx $AGENT_HOME/upload_files  # 기본 ACL(신규 파일 상속)

# api_keys: agent-core 그룹만 rwx, 나머지 차단
sudo setfacl -m g:agent-core:rwx $AGENT_HOME/api_keys
sudo setfacl -m o::--- $AGENT_HOME/api_keys

# /var/log/agent-app: agent-core 그룹만 rwx
sudo setfacl -m g:agent-core:rwx /var/log/agent-app
sudo setfacl -d -m g:agent-core:rwx /var/log/agent-app
sudo setfacl -m o::--- /var/log/agent-app

```

### 권한 확인

```bash
ls -l $AGENT_HOME
getfacl $AGENT_HOME/upload_files
getfacl $AGENT_HOME/api_keys
getfacl /var/log/agent-app

```

### 확인 결과 (예시 출력)

```
# upload_files
# file: /home/agent-admin/agent-app/upload_files
# owner: agent-admin
# group: agent-common
user::rwx
group::rwx
group:agent-common:rwx
mask::rwx
other::---

# api_keys
# file: /home/agent-admin/agent-app/api_keys
# owner: agent-admin
# group: agent-core
user::rwx
group::rwx
group:agent-core:rwx
mask::rwx
other::---

```

---

## 3. 애플리케이션 실행 환경 구성

### 3-1. 환경 변수 설정

`agent-admin` 계정의 `~/.bashrc` 또는 `~/.bash_profile`에 환경 변수를 등록한다.

```bash
sudo -u agent-admin bash -c 'cat >> /home/agent-admin/.bashrc << "EOF"

# Agent App 환경 변수
export AGENT_HOME=/home/agent-admin/agent-app
export AGENT_PORT=15034
export AGENT_UPLOAD_DIR=$AGENT_HOME/upload_files
export AGENT_KEY_PATH=$AGENT_HOME/api_keys/t_secret.key
export AGENT_LOG_DIR=/var/log/agent-app
EOF'

```

### 환경 변수 적용 및 확인

```bash
# agent-admin 계정으로 전환 후 적용
su - agent-admin
source ~/.bashrc

# 확인
echo $AGENT_HOME
echo $AGENT_PORT
echo $AGENT_UPLOAD_DIR
echo $AGENT_KEY_PATH
echo $AGENT_LOG_DIR

```

### 확인 결과 (예시 출력)

```
/home/agent-admin/agent-app
15034
/home/agent-admin/agent-app/upload_files
/home/agent-admin/agent-app/api_keys/t_secret.key
/var/log/agent-app

```

---

### 3-2. 키 파일 생성

```bash
# agent-admin 계정으로 수행
su - agent-admin

# 키 파일 생성
echo "agent_api_key_test" > $AGENT_HOME/api_keys/secret.key

# 권한 설정 (소유자만 읽기)
chmod 640 $AGENT_HOME/api_keys/t_secret.key

# 확인
cat $AGENT_HOME/api_keys/t_secret.key
ls -l $AGENT_HOME/api_keys/

```

### 확인 결과 (예시 출력)

```
agent_api_key_test

-rw-r----- 1 agent-admin agent-core 19 YYYY-MM-DD HH:MM t_secret.key

```

---

### 3-3. 앱 실행 및 Boot Sequence 확인

```bash
# agent-admin 계정으로 전환
su - agent-admin

# 앱 실행
python3 $AGENT_HOME/agent_app.py

```

### 확인 결과 (Boot Sequence 출력 예시)

```
Starting Agent Boot Sequence...
[1/5] Checking User Account               [OK]
... Running as service user 'agent-admin' (uid=1001)
[2/5] Verifying Environment Variables     [OK]
... All required Envs correct
[3/5] Checking Required Files             [OK]
... Verified key file with correct key string.
[4/5] Checking Port Availability          [OK]
... Port 15034 is available.
[5/5] Verifying Log Permission            [OK]
... Log directory is writable: /var/log/agent-app
------------------------------------------------------------
All Boot Checks Passed!
Agent READY

```

### 포트 LISTEN 상태 확인 (별도 터미널)

```bash
ss -tulnp | grep 15034

```

```
tcp  LISTEN  0  128  0.0.0.0:15034  0.0.0.0:*  users:(("python3",pid=XXXX,fd=X))

```

> ✅ **확인 포인트**: 5단계 모두 **[OK]**, "Agent READY" 출력, 15034 포트 **LISTEN** 상태 확인

---

## 4. 시스템 관제 자동화 스크립트 구현

### 4-1. [monitor.sh](http://monitor.sh/) 파일 생성 및 권한 설정

```bash
# 파일 생성
sudo touch $AGENT_HOME/bin/monitor.sh

# 소유자/그룹 설정
sudo chown agent-dev:agent-core $AGENT_HOME/bin/monitor.sh

# 권한 설정: rwxr-x--- (750)
sudo chmod 750 $AGENT_HOME/bin/monitor.sh

# 확인
ls -l $AGENT_HOME/bin/monitor.sh

```

### 확인 결과 (예시 출력)

```
-rwxr-x--- 1 agent-dev agent-core XXXX YYYY-MM-DD HH:MM /home/agent-admin/agent-app/bin/monitor.sh

```

---

### 4-2. [monitor.sh](http://monitor.sh/) 소스코드

```bash
cat > $AGENT_HOME/bin/monitor.sh << 'EOF'
#!/bin/bash

# ==========================================
# Agent App Monitor Script
# ==========================================

AGENT_HOME="/home/agent-admin/agent-app"
AGENT_BIN="$AGENT_HOME/agent-app-linux-x86"
LOG_FILE="/var/log/agent-app/monitor.log"
CHECK_INTERVAL=60

# ------------------------------------------
# 타임스탬프 반환 함수
# ------------------------------------------
get_timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# ------------------------------------------
# 로그 기록 함수
# ------------------------------------------
log_msg() {
    echo "[$(get_timestamp)] $1" >> "$LOG_FILE"
}

# ------------------------------------------
# 앱 실행 함수
# ------------------------------------------
start_agent() {
    source /home/agent-admin/.bashrc
    nohup "$AGENT_BIN" >> "$LOG_FILE" 2>&1 &
    log_msg "Agent started. PID=$!"
}

# ------------------------------------------
# 로그 로테이션 (10MB 초과 시)
# ------------------------------------------
rotate_log() {
    local max_size=$((10 * 1024 * 1024))
    if [ -f "$LOG_FILE" ]; then
        local file_size
        file_size=$(stat -c%s "$LOG_FILE")
        if [ "$file_size" -gt "$max_size" ]; then
            mv "$LOG_FILE" "${LOG_FILE}.1"
            log_msg "Log rotated. Previous log saved as ${LOG_FILE}.1"
        fi
    fi
}

# ------------------------------------------
# 메인 루프
# ------------------------------------------
log_msg "Monitor started."

while true; do
    rotate_log

    if ! pgrep -f "agent-app-linux-x86" > /dev/null 2>&1; then
        log_msg "Agent not running. Restarting..."
        start_agent
    else
        log_msg "Agent is running."
    fi

    sleep "$CHECK_INTERVAL"
done
EOF

```

---

## 5. 자동 실행(cron) 설정

### 5-1. crontab 등록

```bash
# agent-admin 계정으로 crontab 편집
su - agent-admin
crontab -e

```

### 등록 내용

```
# 매분 monitor.sh 실행
* * * * * /home/agent-admin/agent-app/bin/monitor.sh >> /var/log/agent-app/monitor.log 2>&1

```

### 5-2. crontab 등록 확인

```bash
# 등록된 crontab 확인
crontab -l

```

### 확인 결과 (예시 출력)

```
* * * * * /home/agent-admin/agent-app/bin/monitor.sh >> /var/log/agent-app/monitor.log 2>&1

```

### 5-3. 자동 실행 후 로그 누적 확인 (1~2분 후)

```bash
# 최근 로그 라인 확인
tail -20 /var/log/agent-app/monitor.log

```

### 확인 결과 (예시 출력)

```
[2025-01-15 10:01:00] PID:1234 CPU:5% MEM:42% DISK_USED:35%
[2025-01-15 10:02:00] PID:1234 CPU:6% MEM:43% DISK_USED:35%
[2025-01-15 10:03:00] PID:1234 CPU:4% MEM:42% DISK_USED:35%

```

> ✅ **확인 포인트**: 매분 새 라인이 자동으로 누적되는 것을 확인

---

## 필수 증거 자료 체크리스트


| #   | 항목                                     | 확인 명령어                                              | 상태  |
| --- | -------------------------------------- | --------------------------------------------------- | --- |
| 1   | SSH 포트 20022 변경                        | `ss -tulnp \| grep sshd`                            | ✅   |
| 2   | Root 원격 접속 차단                          | `grep PermitRootLogin /etc/ssh/sshd_config`         | ✅   |
| 3   | UFW 활성화 및 포트 허용                        | `ufw status verbose`                                | ✅   |
| 4   | 계정/그룹 생성 확인                            | `id agent-admin && id agent-dev && id agent-test`   | ✅   |
| 5   | 디렉토리 구조 및 권한                           | `ls -l $AGENT_HOME && getfacl $AGENT_HOME/api_keys` | ✅   |
| 6   | 앱 Boot Sequence [OK]                   | `python3 $AGENT_HOME/agent_app.py` 실행 결과            | ✅   |
| 7   | [monitor.sh](http://monitor.sh/) 권한 확인 | `ls -l $AGENT_HOME/bin/monitor.sh`                  | ✅   |
| 8   | [monitor.sh](http://monitor.sh/) 실행 결과 | `$AGENT_HOME/bin/monitor.sh` 콘솔 출력                  | ✅   |
| 9   | monitor.log 누적 확인                      | `tail -20 /var/log/agent-app/monitor.log`           | ✅   |
| 10  | crontab 등록 확인                          | `crontab -l` (agent-admin 계정)                       | ✅   |
| 11  | cron 자동 실행 확인                          | 1분 후 `tail -f /var/log/agent-app/monitor.log`       | ✅   |


---
<img width="883" height="526" alt="스크린샷 2026-05-22 오후 5 37 32" src="https://github.com/user-attachments/assets/1a74c561-e8cc-4a93-be12-885b99433017" />
<img width="682" height="260" alt="스크린샷 2026-05-22 오후 5 38 53" src="https://github.com/user-attachments/assets/66bdaa01-ac6f-4e93-97b0-3dfa441c51b6" />
<img width="567" height="545" alt="스크린샷 2026-05-22 오후 5 43 29" src="https://github.com/user-attachments/assets/b2e73385-e51d-4352-8344-94cb42b2aa97" />
<img width="786" height="996" alt="스크린샷 2026-05-22 오후 5 45 38" src="https://github.com/user-attachments/assets/21aef279-d672-4264-859b-bff9c02bd0e1" />
<img width="652" height="120" alt="스크린샷 2026-05-22 오후 5 55 32" src="https://github.com/user-attachments/assets/096693fc-a731-474e-b0ce-3e255f678207" />
<img width="658" height="936" alt="스크린샷 2026-05-22 오후 6 04 33" src="https://github.com/user-attachments/assets/052f1239-ebba-4f3f-a9e6-dff3b189d1c5" />
<img width="745" height="791" alt="스크린샷 2026-05-22 오후 6 07 47" src="https://github.com/user-attachments/assets/ffe02471-c115-4b50-801f-9d15d4581095" />
<img width="761" height="386" alt="스크린샷 2026-05-22 오후 6 25 07" src="https://github.com/user-attachments/assets/00d0c595-0a2d-499f-b678-a3cb69dcfdb8" />




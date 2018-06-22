# Email System Monitor

通过向该程序发送 Email 来获取当前系统的状态，包括：

- 系统运行时间
- CPU 使用情况及信息
- CPU 温度

另外，该程序还可以通过发送Email实现远程执行命令和关机等功能。

**本程序只支持 Unix 平台。Windows 无法运行该程序。**

---
# 运行本程序

*要运行此程序，你需要 `Python 3` 运行环境。*    

### 其他要求

如果你需要后台运行，你可能还需要 `screen` 程序。

### 运行

克隆本仓库：
```
git clone https://github.com/SpinMrY/Sysmonitor.git
cd Sysmonitor
```
   
确保你已经安装了 `Python 3` ，然后输入：
```
screen python3 ./sysmon.py
```

按下 `Ctrl-A` `D` 以返回当前 shell ，保持后台运行。

# 使用

使用指定邮箱地址发送：
    state           获取系统当前状态并发回指定邮箱
    comnd [命令]    远程执行指令
    shutd           远程关机
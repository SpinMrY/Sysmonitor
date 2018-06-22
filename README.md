# Email System Monitor

通过向该程序发送 Email 来获取当前系统的状态，包括：

- 系统运行时间
- CPU 使用情况及信息
- CPU 温度

**本程序只支持 Unix 平台。Windows 无法运行该程序。**

---
# 运行本程序

*要运行此程序，你需要 `Python 27` 运行环境。*    

### 其他要求

如果你需要后台运行，你可能还需要 `screen` 程序。

### 运行

克隆本仓库：
```
git clone https://github.com/SpinMrY/Sysmonitor.git
cd Sysmonitor
```
   
确保你已经安装了 `Python 2.7` ，然后输入：
```
screen python ./sysmon.py
```

按下 `Ctrl-A` `D` 以返回当前 shell ，保持后台运行。

# 使用


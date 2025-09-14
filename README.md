

1、windows和office激活 来自[这里](https://github.com/massgravel/Microsoft-Activation-Scripts)

 PowerShell 下运行命令  

 ```
irm https://get.activated.win | iex
```



2、安装类似macOS的mojave动态桌面
下载mojave.xml文件及动态壁纸文件 到指定的文件夹并解压
修改mojave.xml文件，将其中的壁纸文件路径修改为指定文件夹壁纸路径
在优化-外观-背景图像里选择mojave.xml文件即可。

3、 安装Open WebUI  docker-compose.yml 文件

 ```
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "3001:8080"
    environment:
      - ENABLE_WEBSOCKET_SUPPORT=false
      - ENABLE_MODEL_WHITELIST: "false"

    volumes:
      - ~/openwebui:/app/backend/data
    restart: always
    network_mode: bridge
    expose:
      - "8080"
volumes:
  open-webui:
```

4、用winsw软件设置sing-box开机启动
下载 WinSW-x64.exe到sing-box目录，然后重名为 winsw.exe  下载地址（https://github.com/winsw/winsw/releases） 
在sing-box的目录下创建 winsw.xml 内容如下
 ```
<service>
<id>sing-box</id>
<name>sing-box</name>
<description>This service runs sing-box continuous integration system.</description>
<executable>D:\sing-box\sing-box.exe</executable>
<arguments>run -c D:\sing-box\config.json</arguments>
<log mode="reset"/>
<onfailure action="restart"/>
</service>
```
powershell里切换到sing-box目录下
```
  ./winsw.exe install   
  ./winsw.exe start   
```

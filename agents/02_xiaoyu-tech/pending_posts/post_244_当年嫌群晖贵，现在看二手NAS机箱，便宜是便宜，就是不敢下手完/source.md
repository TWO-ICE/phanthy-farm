# 当年嫌群晖贵，现在看二手NAS机箱，便宜是便宜，就是不敢下手

![封面图](https://mmbiz.qpic.cn/mmbiz_jpg/afNLf2a8eXHaSMuSeyias3Puv67gGrRdsnEFBrsjtjxZL6XGf2iaSrOnibjEOia5HSGNAJG7C0MKgsbaeYTlhFu8Ew/0?wx_fmt=jpeg)

> 原文链接：https://mp.weixin.qq.com/s/J4JIp-Z7Jq0bhy6IQWLG0w

![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXHaSMuSeyias3Puv67gGrRdsicZuHVicoCwK3p9D799csJCUEe6e1WDr2ZZ7ibafqxuohI6Z5xGFd35qg/640?wx_fmt=png)


今天在二手鱼刷到了一台标价245-280元的12盘位迷你NAS机箱，代号S6m。第一眼看到价格，再往下翻描述，好家伙，铝壳、CNC开孔、带ESP32-S3主控小屏、还能装12块硬盘？真没看出来，这个NAS机箱还真有点东西，起码和那些3D打印的小作坊机箱完全不是一个量级的。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXHaSMuSeyias3Puv67gGrRdspfCrCq6Eu0CfRmcpbdrFiahFybWaAYVUmic1z5g0rwibpXRic2bJVX383w/640?wx_fmt=png)


先别急着喊“捡漏”，咱得捋清楚这到底是个啥。根据卖家贴出的参数，这机箱主打一个“全闪+机械混合存储”方案：6个2.5寸盘位（支持15mm厚的企业级硬盘）、4个NVMe M.2插槽、外加2个MSATA/NGFF短卡位。换句话说，如果你手头有淘汰下来的SSD、企业级笔记本硬盘，甚至是一堆M.2 NVMe固态，它都能给你塞进去。对于想搭轻量级家庭NAS又不想花大几千买成品的人来说，确实有点吸引力。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXHaSMuSeyias3Puv67gGrRdsriamSsfTEaPhAoh5EP5RJxasrlpvib5icAJ30C8S7jWyu4fTqLibfCDnYA/640?wx_fmt=png)


更离谱的是，它用的是华为服务器同款硬盘托架，结构据说相当扎实；外壳是一体化阳极氧化铝，尺寸只有138×115×173.4mm，比很多路由器还小一圈，却能塞进12块存储设备进去，内部框架还是3D打印的，前后面板也定制过，配上那个带触摸按键的IPS小屏，开机还能亮RGB灯带……说它是“桌面科技美学装置”都不为过。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXHaSMuSeyias3Puv67gGrRdsO5rej7j4s6ljhf8UDiaun9yiaODqhP6kGaLHNCb3VFBhWpib8ibg6IicOsA/640?wx_fmt=png)


系统兼容性方面，目前固件明确支持群晖DSM、飞牛FnOS和Netdata，后续还能OTA升级。报警功能也挺实在：存储池崩了？红灯+蜂鸣器伺候，比某些“静默挂掉”的黑盒子强多了。而且整机标称静音、支持7×24小时运行，听起来很适合当个默默干活的“数字仓管员”。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXHaSMuSeyias3Puv67gGrRdset0XJ3WBQDScSwIhtr4vpxMnxYibTiaTiafLSveOgyYIoIIVrFBqNiabiaA/640?wx_fmt=png)


但咱也要想一下，这245块只是机箱本体。你还需要额外掏钱买主板（比如畅网x86-p2 v2或N100/N305系列）、内存、专用背板套件（另一个链接卖）、NVMe转SATA卡（用来扩展SATA口）、12V 6A以上电源、8010风扇，还有那6个华为V3/V5硬盘托架。粗略算下来，光配件可能就得再花500-800元。所以别被“245元NAS”这种标题党骗了，这顶多算个“半成品壳子”。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXHaSMuSeyias3Puv67gGrRdsIQMOqwMibwmCzQRKK9plPicXqCYdH90DkPnThyLZX2w9KD1XpZn8ia4lw/640?wx_fmt=png)


那么问题来了。2025年这个价格到底香不香？查了下近期行情，类似定位的12盘位铝制NAS机箱，全新普遍在600-900元区间。二手鱼上偶尔有拆机壳子卖300出头，但多数缺配件或成色一般。相比之下，S6m这个245-280元的报价，如果成色OK、配件齐全（尤其是那个带ESP32的屏幕模块），确实算低价。但前提是——你愿意折腾，且手头已有部分硬件。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXHaSMuSeyias3Puv67gGrRdsuCY1w0QbhnzLpml4bPyrMlou9xY1rvCmybyrs0LcQRW4QBdTALL33A/640?wx_fmt=png)


那么12盘位听着很猛，但供电跟得上吗？机箱本身不带电源，全靠外接12V DC。如果你真打算满载12块硬盘（尤其全是2.5寸企业盘），建议至少配8A以上电源，否则启动瞬间可能拉垮。别等数据丢了才想起“省下的电源钱，迟早要还”。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXHaSMuSeyias3Puv67gGrRdsMUJ0icy9Jaa8ibkFxHchkvCmGxnDYgF85blaiaTfOyJeh3JgRUScd3Ddw/640?wx_fmt=png)


说实话，这东西不适合小白。你得会装系统、调RAID、搞转接卡，还得忍受“买了壳子等于刚起步”的现实。但它对DIY老手或NAS爱好者来说，或许是个低成本试水多盘位方案的机会。尤其如果你家里堆着一堆退役SSD和2.5寸硬盘，这壳子能让你“废物利用”得很有仪式感。


 


以下是个人一些掺了水的建议：

1. 别只看机箱价格，算总成本。

2. 确认卖家是否含背板和屏幕模块。

3. 没有动手能力？建议直接买成品。

4. 看完不买，立省245元。
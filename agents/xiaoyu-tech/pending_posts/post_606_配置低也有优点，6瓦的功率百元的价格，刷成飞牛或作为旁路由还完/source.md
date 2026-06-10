# 配置低也有优点，6瓦的功率百元的价格，刷成飞牛或作为旁路由还是挺香的！

![封面图](https://mmbiz.qpic.cn/mmbiz_jpg/afNLf2a8eXGI67HXFm7asD0W393BeqdoNqkmarRrSL3Cjo8C4a8BzQ3YlM3Jt4htdM5EjTtDyfSc7c4svia0DMA/0?wx_fmt=jpeg)

> 原文链接：https://mp.weixin.qq.com/s/31yi9UO7ERy00TFkP-f0EA

![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXGI67HXFm7asD0W393BeqdoOI6f16czm3vP4P3b87JhMXAVwxDruNNKV5MH5DyClX1B8h2MnNsFCg/640?wx_fmt=png)


最近因为固态硬盘和内存条价格疯涨，不少网友开始把目光转向二手平台淘老设备搭轻量NAS或者做远程控制终端。我淘到一款105元的N3010三盘位小主机，铝合金外壳、手掌大小，看着挺精致。这款机器正好打着“适合飞牛NAS”“可装Linux”的标签。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXGI67HXFm7asD0W393BeqdoHItyicZ7Dric221cSJ5KAx4L00qTiaribgicYic0XBYXInicYk4r6kao5JdYg/640?wx_fmt=png)


卖家描述里提到，这台小主机型号是KRAMER VIA GO，搭载的是Intel N3010处理器，内存是2GB DDR3笔记本条，内置32GB eMMC存储，勉强够装个精简版Win10或飞牛。好在主板预留了M.2 2230插槽，还能通过20pin SATA一体线接一块2.5英寸SATA硬盘，加上两个2.5寸盘位和一个M.2，确实算得上“三盘位”。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXGI67HXFm7asD0W393BeqdotIIkhhficHC0DLkNa4YAoWIpfs3FXPqXEZmzpoQHTtDiawnNwS9LJYIg/640?wx_fmt=png)


不过得注意，2GB内存是硬伤。即便装轻量Linux发行版，开几个Docker容器就可能爆内存。如果真想跑飞牛NAS这类国产系统，2G有些吃力，最好把内存上到8G。另外，N3010的I/O能力也有限：仅一个千兆网口、两个USB 3.0、HDMI输出，无线靠的是老旧的AC3168网卡，速度和稳定性都不如现在主流的AX系列。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXGI67HXFm7asD0W393Beqdo1v9NQkq2ic6sqzuvlatfJ6fgUowjpkfxFG0AdHtZPXWgLdgHHOSSLVw/640?wx_fmt=png)


那么问题来了105元贵不贵？在存储芯片价格翻倍的这个节点，全新1TB SSD要七八百，16GB DDR4内存条四五百，相比之下，这台带电源、金属壳、三盘位扩展的小主机似乎显得“性价比突出”。但理性来看，它的核心短板在于性能和扩展性天花板太低。如果你只是需要一个7×24开机的下载机或远程SSH跳板，它或许够用；但若指望它承担家庭多媒体中心、多用户文件服务，那大概率会失望。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXGI67HXFm7asD0W393BeqdoibYCuBBxpxAdkCnqUFTFiaMqwCNekXd3bNayb08IeB46cIRjwfNejWXw/640?wx_fmt=png)


可能有人会问：“这机器能刷飞牛NAS吗？”可以安装但体验堪忧。飞牛对硬件虽无强制要求，但社区普遍反馈2GB内存下系统会卡顿。更现实的用途可能是装OpenWrt做旁路由，或者跑个轻量Web服务。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXGI67HXFm7asD0W393Beqdok0LDichqrnfVt1ufdEjat4siaicb1H4SCfYhD5kTNMrrDrVdheOcm3cTQ/640?wx_fmt=png)


要说优点的话，除了价格不算太贵之外，功耗也算是一个亮点。卖家给出了实测图，功率只有6W，属性相当省电的范畴，这个功率和家里的路由器差不多，一天也就几毛钱的电费，所以它适合24小时开机。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXGI67HXFm7asD0W393BeqdoibibcQRdTAwoP43jIU8oGibGYzKH42DibkYjpKO2zDcOicVDH3DGO67olfA/640?wx_fmt=png)


对此产品有兴趣的话，可以在二手鱼搜索“N3010三盘位小主机”这个关键字就可以找到此产品，如果找不到可以通过图片进行搜索，都搜索不到的话，那可能是此产品已卖出或者是下架了。


 


以下是个人一些掺了水的建议：

1. 仅适合极简服务或学习Linux使用。

2. 别指望它替代正经NAS或主力服务器。

3. 若已有闲置配件，105元可小试；否则慎入。

4. 看完不买，立省105元。
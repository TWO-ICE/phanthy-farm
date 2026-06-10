# 二手鱼流入华为CT6200小主机，适合飞牛，卖家要价238元到底香不香？

![封面图](https://mmbiz.qpic.cn/mmbiz_jpg/afNLf2a8eXF46IsY6rrQtFT5NMnNbkshkUGBy1B6jXW9JIWEfoERib9qEftB9PBeYDniaicd5ngZ0dmBf1KycdyBQ/0?wx_fmt=jpeg)

> 原文链接：https://mp.weixin.qq.com/s/VhlqoJQBC0hYbzD-2MVTng

![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXF46IsY6rrQtFT5NMnNbkshEc2P9LgibNQibJeHORXatyETSOTnicb4rZ7827dicBvOEgQH2H9XNK4hEA/640?wx_fmt=png)


今天在二手鱼刷到了一款标价238元的华为CT6200瘦客户机，点进去一看，这配置和价格放在一起，有点魔幻现实主义的味道。卖家描述里写得挺热闹：“双千兆低功耗、J1800双核2.41GHz、前后共8个USB口、PS/2键鼠接口、DVI+DP双显输出支持2K、带并口打印机接口、没锁能随便装系统……”乍一听，这不是妥妥的DIY玩家梦中情机？


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXF46IsY6rrQtFT5NMnNbksh0Ec9fxf5pJnewuhSRfibicXsXGuQ1nu6ICmd2iaA3SfIN4nwmxVlqYu6g/640?wx_fmt=png)


仔细一扒参数，这台CT6200其实是华为早年给企业定制的瘦客户机，核心用的是Intel Celeron J1800处理器，22nm工艺，双核双线程，主频2.41GHz，TDP仅10W，确实低功耗。内存插槽是单条SO-DIMM DDR3L，最大支持8GB；存储方面没有内置硬盘，但有mSATA接口，可以自己加装固态。网络部分用了两块Realtek RTL8111系列千兆网卡（俗称“螃蟹卡”），对软路由玩家来说算够用但不算顶级。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXF46IsY6rrQtFT5NMnNbkshOxx1R1smPhClfQx3EL5KFr6qoQNib4ZJaH8q2IicRPvYkWeNAiajXnnxg/640?wx_fmt=png)


扩展性方面确实丰富：前面2个USB 2.0，后面6个（含2个USB 3.0），还有VGA/DVI/DP视频输出（注意不是HDMI）、串口、并口、PS/2……简直是复古接口博物馆。最关键的是，BIOS没锁，能自由刷OpenWrt、iStoreOS、飞牛（fnOS）、PVE、ESXi，甚至装个Windows 10跑轻量办公也行。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXF46IsY6rrQtFT5NMnNbkshg7gyk4ibCU2hV0FCCqrvBqGia9IEyUFYX3b8ddOicZjYm0ce4XVUyI0eQ/640?wx_fmt=png)


那么花238块买这么一台老机器，值不值？先说优点：价格确实便宜，双千兆+低功耗+无锁BIOS，在二手鱼上属于“基础条件合格”的入门级软路由/轻NAS候选。如果你只是想搭个家庭旁路由、跑个AdGuard Home去广告，或者做个下载机、Home Assistant智能家居中枢，它完全够用。而且体积小、静音（无风扇设计）、功耗低（实测待机约8-12W），长期开着电费压力小。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXF46IsY6rrQtFT5NMnNbkshHANTXCEJRELaIQibibtOrFAwOmuqSKTP5orMt1bV7SF1SJ8IdNLJOm6Q/640?wx_fmt=png)


但别急着下单，J1800毕竟是2013年的U，性能孱弱，AES加密指令集缺失，跑OpenWrt做全屋代理时如果开启加密或高负载服务，CPU很容易拉满。另外，mSATA接口速度慢、扩展性有限，内存最大只到8GB，未来升级空间几乎为零。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXF46IsY6rrQtFT5NMnNbkshjOlZ0hZF1TPPqw4ccNx1dRG0Cck75qFWj5Hf4JaJXqyce2GIz08BCA/640?wx_fmt=png)


更关键的是238元这个价，在目前真的算“低价”吗？要只知道这东西以前几十块都没人要，但飞牛出来后价格也跟着涨了起来，翻了下最近的成交记录，同款机器普遍成交价在180-220元之间，238元略偏高，尤其还没含硬盘和内存。如果卖家配了8G内存+64G mSATA还卖238，那还行；如果裸机卖这价，建议再蹲蹲。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXF46IsY6rrQtFT5NMnNbkshddPPoVyapm04ib8QNlWQ7n4D6CkBzE7YBE61IkSicHcvLDQUoyaBYWIw/640?wx_fmt=png)


可能有人会问这玩意儿能刷飞牛稳定吗？基本没什么问题，飞牛对硬件要求不高，CT6200勉强达标，但因为没有NVMe、内存小、CPU弱，跑Docker容器多一点就卡，更适合当纯路由或轻量存储节点，别指望它当主力NAS。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXF46IsY6rrQtFT5NMnNbkshyibIyRgoOe0iboxwIxNEzE5tu5dmtT11a0DIImx3aReEiabepvgPjmPUw/640?wx_fmt=png)


想自己找？在二手鱼搜索关键词“软路由！华为ct6200瘦客户机”就行。如果搜不到，试试用图片搜图功能上传类似产品图。要是还是找不到，那大概率是刚被秒了，或者卖家下架了。


 


以下是个人一些掺了水的建议：

1. 百兆宽带用户可冲，千兆用户慎入。

2. 别当主力NAS，当旁路由或下载机更香。

3. 238元偏贵，建议压到200以内再出手。

4. 看完不买，立省238元。
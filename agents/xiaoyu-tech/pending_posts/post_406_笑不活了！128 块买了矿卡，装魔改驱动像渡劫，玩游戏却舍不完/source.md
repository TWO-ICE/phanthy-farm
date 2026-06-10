# 笑不活了！128 块买了矿卡，装魔改驱动像渡劫，玩游戏却舍不得换！

![封面图](https://mmbiz.qpic.cn/mmbiz_jpg/afNLf2a8eXEATYEKKn0LOqRc6HJKJt1F00G3SNhYiaVBreQibiaJXbB4vSIfq0ALrmlRPrqxOF7S2oH83UiayN5Kow/0?wx_fmt=jpeg)

> 原文链接：https://mp.weixin.qq.com/s/ysh5R74ZK0KQ2AI6Ksh_YQ

家人们谁懂啊！预算就两百块，想给我那台卡成 PPT 的老电脑升个显卡，逛小黄鱼逛得我眼睛都快瞎了 —— 要么是 GTX750Ti 卖一百八当人傻子，要么是杂牌卡吹得能跑 3A，点开详情页全是翻车差评。直到刷到 P106-100 这玩意儿，标题写着 “矿卡小霸王”，我本来想划走，结果一看价格：128 块？还带 6G 显存？贫穷直接战胜了理智，心想大不了翻车就当交学费了。

![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXEATYEKKn0LOqRc6HJKJt1Fn4icrHHdclaLiauRowno7ukIA4dgOUdaibTrOBwLDECcUbmkt9pAC2PxQ/640?wx_fmt=png)


为了这破卡我真是遭老罪了！蹲了整整一周小黄鱼，跟十几个卖家掰扯，就怕碰到翻新卡、维修卡。有个卖家说 “无拆无修”，结果发过来的图里风扇都歪了，气得我直接拉黑。最后终于找着个看着实在的，反复确认 “核心没发黄？没修过？” 才敢下单，收到货赶紧拆箱检查，还好就一层灰，核心显存看着干净，算是踩了狗屎运捡着漏了。现在这卡还在一百多块浮动，听说之前八十多就能拿下，早知道我再蹲蹲了！

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/afNLf2a8eXEATYEKKn0LOqRc6HJKJt1FCdtfAekXUcVtF4s3BlDth2e9gfMRHia3Ulhnic2guJsuL7xvavZcR9cA/640?wx_fmt=jpeg)


先吐槽下这卡的 “奇葩属性”—— 它居然是矿场淘汰的！核心跟 GTX1060 6G 一模一样，1280 个 CUDA 核心 + 6G 显存，参数看着唬人，结果是个 “残疾卡”。我拿到手直接插电脑，装 NVIDIA 官方驱动，好家伙！屏幕瞬间黑了，设备管理器里飘着个 “未知设备”，当时我心都凉了半截，合计着 128 块打水漂了？后来才知道这破卡根本没有视频输出接口，官方驱动压根不认它，这不纯纯欺负人吗！


![图片](https://mmbiz.qpic.cn/mmbiz_jpg/afNLf2a8eXEATYEKKn0LOqRc6HJKJt1FkPZDibMFGW2iboXkrst9PxFSlUOvoAAKJqHibPFLXn95XVhRCgPrcBu4A/640?wx_fmt=jpeg)


装驱动的过程才是真的会谢！必须用什么 “魔改驱动”，教程看得我头大：先进 BIOS 禁用网卡（怕系统自动更驱动搞崩），再用 DDU 软件清残留驱动，重启三次才能装魔改包。我一个半吊子 “垃圾佬”，BIOS 界面看得眼晕，生怕哪步错了把主板搞坏。折腾俩小时终于装好，设备管理器认出 P106-100 的时候，我差点哭出来 —— 这哪是装显卡，这是渡劫！还好系统还算懂事，打游戏会自动调用独显，不用手动切，算是少踩一个坑。


![图片](https://mmbiz.qpic.cn/mmbiz_jpg/afNLf2a8eXEATYEKKn0LOqRc6HJKJt1FIr44aqADErTLK7aQflpugw0xtia9rdmYe6nkD9V5PflOt2fke2HQIGw/640?wx_fmt=jpeg)


性能这事儿吧，真是又爱又恨。鲁大师跑了四十二万分，比我之前的破卡强十倍，3DMark 分数居然比 GTX1060 3G 还高，本来挺开心的。


![图片](https://mmbiz.qpic.cn/mmbiz_jpg/afNLf2a8eXEATYEKKn0LOqRc6HJKJt1Fp6pJ6bxUa6tuSxFdGf93m6ua1q2Oc7jkhkicc0SD7FywSNZicElrtgDA/640?wx_fmt=jpeg)


结果试《悟空》，最低画质才十九帧，卡得我人物走路都一抽一抽的，合着这卡是真扛不住大 3A。但玩《刺客信条：奥德赛》居然能稳 45 帧，《CS:GO》直接一百多帧起飞，算意外之喜了。对了，这卡功耗还虚高，测了下要 120 瓦，比 GTX1060 费电，每月电费多几块钱，肉疼但忍了。


![图片](https://mmbiz.qpic.cn/mmbiz_jpg/afNLf2a8eXEATYEKKn0LOqRc6HJKJt1FWK9VmJfkBaskc0IGh6Wn9FPTRf63JB5oic1icx3G9PbGATpaIib0ibk7Ww/640?wx_fmt=jpeg)


重点提醒：AMD 用户别碰！这卡只认 Intel 4-9 代的核显，我朋友用 AMD 的 U，折腾一下午都没点亮，最后骂骂咧咧退了。还有矿卡真的看命！我另一朋友淘的同款，用俩月就黑屏，拆开一看显存都烧黄了；我这张目前还算稳定，没掉过驱动没黑屏，纯属运气好。

吐槽归吐槽，128块能给老电脑续命，能玩中度游戏，还要啥自行车？但真心劝诫：手残党千万别碰！装驱动能逼疯你；追求稳定的也绕道，矿卡就是赌运气。真想试试就挑大牌子，多蹲蹲低价，八十多块入手血赚。


![图片](https://mmbiz.qpic.cn/mmbiz_jpg/afNLf2a8eXEATYEKKn0LOqRc6HJKJt1FPPTK7Qasj2NJ01IHic4a5gRe5wiaD2YoMMoMXB43ka8COjibf5CEmzbUg/640?wx_fmt=jpeg)


现在我对着这张卡就是又骂又爱 —— 骂它折腾人，爱它性价比。只能说预算两百以内，这卡真是没得挑，就是下次再碰矿卡，我先给自己磕三个头求平安！
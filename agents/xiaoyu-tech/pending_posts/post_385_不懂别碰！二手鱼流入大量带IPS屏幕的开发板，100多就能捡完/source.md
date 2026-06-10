# 不懂别碰！二手鱼流入大量带IPS屏幕的开发板，100多就能捡漏

![封面图](https://mmbiz.qpic.cn/mmbiz_jpg/E9h3abOJCek6wiburjdhP6jshYxwAYEDenfVxWGrldgGv94DBJvqKdUuL3xBicZlzIHj0UQJ8sXSrwlsdsIUMksXmkdQFRjB62uFdeGvDiablU/0?wx_fmt=jpeg)

> 原文链接：https://mp.weixin.qq.com/s/mayTpR2FchjPA9qFs_khSg

一块带IPS屏的Linux开发板，你觉得值多少钱？五百？一千？如果我告诉你，现在只要154元还包邮，你会不会立刻想去“二手鱼”里搜一下？没错，这就是最近圈子里小范围讨论的一个东西，基于NXP i.MX6UL核心板的开发套件，带了一块1.3寸的IPS屏一起卖。这个价格，在如今连树莓派Zero 2W都涨上天的年代，简直像一股清流。


![图片](https://mmbiz.qpic.cn/mmbiz_png/E9h3abOJCelUlE7JqxMUf3yNCQibnBtibMNgSQ8u4t8S6cwS04RkTgVHBAiad6naGhLrfZdk24xS4m4RFKJ4fglAc0FV7gFtz2E4ricB1hdQXiaI/640?wx_fmt=png)


先别急着兴奋或鄙视，我们客观看看这东西。核心是飞凌的i.MX6UL核心板，512MB DDR3内存，8GB EMMC存储。主控就是那个在工控、物联网领域服役多年的老兵NXP i.MX6UL/ULL系列。性能别指望它跑桌面或者看4K，它的战场不在这里。


![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/E9h3abOJCelLxXshFvZw6rDC0R8DdFAua7PBrAxx5y6l1ib5woZsw7UwPYHkSLYSBVXZRT0Fs74rh8TtawquWgZKZCZjyeQpNsT4QPYa4zqY/640?wx_fmt=png)


它的亮点很明确：板载了CH340串口芯片，插上USB线就能调试；自带一个USB-C口用于下载系统；还配了8188EU无线网卡和TF卡扩展。当然，最吸睛的就是那块1.3寸、240*240分辨率的IPS屏了，虽然小，但五脏俱全，直接让这个开发板变成了一个可以独立显示信息的微型终端。


![图片](https://mmbiz.qpic.cn/mmbiz_png/E9h3abOJCeknSGXtWWCBqRXibGDqa0jhWeRvayal1N5kVep0OEGSBOsYSeRIm6C7VN96sGJztZkWD7IF48woK7qRQfMXrmicicMDdnZDSVtuP8/640?wx_fmt=png)


为什么说它有意思？首先当然是价格。154元，可能只是一顿简单的聚餐费用，现在却能买到一个功能完整的ARM Linux开发平台，还带屏。这简直就是为垃圾佬和预算极度抠搜的学生党、入门极客量身定做的。


![图片](https://mmbiz.qpic.cn/mmbiz_png/E9h3abOJCekm5n0e9Z5SlAvT2yMTEPXXjJonBHHmPib5bMHtkicFK8WDOuInhXhQPqw9ibL9P5XNl7EePkdgmI4tg1tSiaCKKnUgqeSicQzLHVuE/640?wx_fmt=png)


其次，卖家提供了内核源码、烧写工具和原理图，并且提到可以参照正点原子的教程学习。这意味着学习路径是清晰的，降低了入门门槛。对于想学习嵌入式Linux驱动开发、QT图形界面编程，或者单纯想搞个网络监控屏、智能家居中控显示终端的人来说，它提供了一个极低的试错成本。


![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/E9h3abOJCenne6ASicvMkf4G9shxTYWbC7mU28WGictoe2vrOyria8nwpfbibjVgTSRibEhbeWDDicthibjKsDHXxgfBaTjNDZic4icrPckib6st3lwM0/640?wx_fmt=png)


但是，老铁们，别急着“果断出手”。i.MX6UL的性能在今天看来确实孱弱，它是为低功耗、实时性设计的，不适合做复杂应用。那块1.3寸的屏幕，玩一玩可以，真想做个像样的UI，面积和分辨率都是巨大的限制。所以，它绝对不适合小白盲目跟风，如果你连Linux命令行都还没熟悉，我劝你谨慎，它很可能在你手里吃灰。


![图片](https://mmbiz.qpic.cn/mmbiz_png/E9h3abOJCenRYoWjOJDh73nUPnOSmS7xYGuWQickH0mmfREHupB4unew4qYJQ8IDcZJZhd2vj2tYpvpJK3WOkN2Veu52GhebCjk3vLgxzCe4/640?wx_fmt=png)


那么，它适合谁？我脑海中立刻浮现出几个场景：一个是电子专业的学生，想花最少的钱，亲手操作一下从uboot、内核到根文件系统的完整移植过程，这块板子硬件接口标准，资料相对齐全。另一个是极客玩家，想把它改造成一个桌面式的迷你服务器状态监控屏，实时显示CPU温度、网络流量，或者作为一个智能家居的轻量级控制面板。甚至，你可以把它当作一个超低成本的网络协议栈测试平台。


![图片](https://mmbiz.qpic.cn/mmbiz_png/E9h3abOJCemfYPgCD9lA0QvCdcq4wLalkQicibVrA7saSgepH38EYOMPICPqzeHHibzjYI1KRALfuVonFw3buj13S0ue12M0FK7YJibkjjSRrtU/640?wx_fmt=png)


最后想问问大家，你们还遇到过哪些让你惊呼“价格被打下来了”的电子好物？或者，对于这样一块板子，你脑海中已经有了什么有趣的改造项目？欢迎在评论区分享你的“神构思”，或者晒出你的踩坑经历，让我们一起在“捡漏”的路上少走弯路！
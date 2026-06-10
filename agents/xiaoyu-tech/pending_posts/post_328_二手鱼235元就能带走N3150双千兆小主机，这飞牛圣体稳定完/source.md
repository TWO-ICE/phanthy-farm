# 二手鱼235元就能带走N3150双千兆小主机，这飞牛圣体稳定的很

![封面图](https://mmbiz.qpic.cn/mmbiz_jpg/afNLf2a8eXGUeeyibgryNaKDMJVJGFGiaMfDDfIYnuFO81uMtNZs3qy1AycazIa7RkeTNRPLtNsL5UbicO2VCClHQ/0?wx_fmt=jpeg)

> 原文链接：https://mp.weixin.qq.com/s/xnl85vchLT3WoFLhiNJ0zA

![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXGUeeyibgryNaKDMJVJGFGiaMpVVoqiawqekmadAE95LzZbX5riaHv8fda7fytCFFD2DWVE5PJLHjYNJQ/640?wx_fmt=png)


今天在二手鱼刷到了N3150双千兆小主机，标价235元还包邮，配置是4G内存+64G mSATA固态，成色看着还行，有使用痕迹但没大毛病。看到这个价格我差点以为卖家把“2”打成了“3”——毕竟当年这玩意儿可是正经的工控/嵌入式平台，现在居然白菜价甩卖，简直像在电子垃圾堆里捡到一块金表。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXGUeeyibgryNaKDMJVJGFGiaMYicrrHFn51mAbWIUsFyHGIDlNpISZQBzuicKmE21ycm1xLOnYAKibLCIQ/640?wx_fmt=png)


先说说这台小主机的底子。CPU用的是Intel N3150，四核四线程，主频1.6GHz（睿频最高2.08GHz），TDP只有6W，妥妥的低功耗选手。别看它年纪不小（2015年左右发布的），放在今天跑个轻量级NAS、软路由、HTPC或者下载机完全没问题。尤其适合折腾飞牛系统（fnOS）——网上一堆老哥拿它当主力下载机，安静又省电，插上电几乎听不到声音，因为压根没风扇，全靠金属外壳被动散热。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXGUeeyibgryNaKDMJVJGFGiaM7ibAicicPnJdhMAbz3roDFmhiaXKlTa9Id40QcY6zms5bHNJF7rR6ldFlA/640?wx_fmt=png)


再来看扩展性。机身约17×13×3.7cm，重0.7kg，接口却挺实在：两个千兆网口，都是Realtek RTL8111芯片，做双网口软路由或者链路聚合刚好；一个SATA接口接2.5寸硬盘，一个mSATA插槽装系统盘，还有一个mini PCIe槽位（可惜不能直接插WiFi模块，得转接）。内存方面只有一条DDR3L笔记本内存插槽，最大支持8GB。供电是常见的12V 5.5×2.5mm圆口，卖家另配12V3A电源的话加13块，不算坑。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXGUeeyibgryNaKDMJVJGFGiaMOkYXf56rOl7Hvia8G9H8fFN8ECMb4Mja2a8icTgFicbpY8Ex4MovGhAZw/640?wx_fmt=png)


N3150当年可是迷你PC和工控领域的香饽饽。x86架构、双网口、低功耗、稳定性强，很多企业拿它做瘦客户机或边缘计算节点。如今虽然被J4125、N5105这些新U吊打，但胜在便宜、驱动成熟、社区支持多。尤其在飞牛圈子里，它被戏称为“飞牛圣体”——不是因为它多强，而是因为便宜耐造、折腾成本低，坏了也不心疼。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXGUeeyibgryNaKDMJVJGFGiaMJ2rs0LjawRkv8MS7BHufI8Fkib7icgGxKwoicib2TC9ia2n2URRqd1NeWMw/640?wx_fmt=png)


可能有人会问：“这配置跑飞牛系统够用吗？”其实是完全够的。飞牛对硬件要求不高，4G内存+64G系统盘起步就行。N3150虽然老，但x86架构兼容性好，官方镜像直接支持，装完基本功能全开，做影音库、自动下载、内网穿透都稳得很。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXGUeeyibgryNaKDMJVJGFGiaMC7ibUWbU951eqSkznCkn7MA2PouEIQYHzxEPaLz77WiaKJJF52yggqibQ/640?wx_fmt=png)


那么双千兆网口能做软路由吗？能，但别指望高性能。日常家用千兆宽带跑满没问题，不过如果打算跑OpenWRT+广告过滤+科学上网三件套，可能会有点吃力。但对于百兆宽带用户或者纯内网分流场景，它绰绰有余，关键是功耗才5-6瓦，电费几乎忽略不计。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXGUeeyibgryNaKDMJVJGFGiaMGFJjRheVibfPQfjgh1rBUmQRMzYicthrg4tib3icGPriaIqAUXTW0KgaiazQ/640?wx_fmt=png)


最后提醒一句：这种老设备水很深。有的卖家把坏掉的板子翻新后当“工控机”卖，有的内存焊死不能升级，还有的SATA接口虚焊。所以下单前务必确认：能不能开机？有没有坏道？网口是否都正常？最好让卖家拍个进系统+测速的小视频。这个价格还要啥自行车？只要机器能点亮、接口全活，235元真的可接受，性价还行。


![图片](https://mmbiz.qpic.cn/mmbiz_png/afNLf2a8eXGUeeyibgryNaKDMJVJGFGiaMJZAe0568zuptGqGQQIHMNcXB2dC8keuBoav3L1kCngSiaWwJvbPvzAw/640?wx_fmt=png)


如果你也在二手鱼蹲这类老平台小主机，不妨留意下关键词：“N3150”“双千兆”“无风扇”“4+64”。说不定下一个捡漏的就是你。老规矩，看完不买，立省235元。
# 昔日跑宽带的边角料，现在变成159元的飞牛圣体，接盘侠在哪？

![封面图](https://mmbiz.qpic.cn/sz_mmbiz_jpg/E9h3abOJCen8Xic0SYY9FyZhHG9lic1JNnSpFTB8c3pM6EiasoWDhedKbBCaQXsX5AWVduUv8SwI1I3ibqTKop4Kebx74icTpyic2VIKEEYXTlXsQ/0?wx_fmt=jpeg)

> 原文链接：https://mp.weixin.qq.com/s/aXJ7RS8pQautqCK-a_2C-Q

二手鱼里刷到个飞牛主机，卖家标价159元。这玩意儿我之前见过，就是前两年跑宽带业务的边缘计算盒子。卖家描述里写的是六核A311D处理器，4G内存加8G存储，还能装三块2.5寸硬盘，配件齐全无拆修，已刷好飞牛系统，插电就能用，卖家还特意强调不是矿渣。


![图片](https://mmbiz.qpic.cn/mmbiz_png/E9h3abOJCek54d4kicymlJ9tbnyHzl6RiaTX6IibVMzRZ102TXic3SRo0o5VIMvDMSP33CqEMC2n3RAo8AAKZ85t5WqudfhBMVoToZkQOp9rGgA/640?wx_fmt=png)


这价格看着确实有点意思。A311D这颗芯片是Amlogic的旗舰级SoC，采用12nm工艺，四颗Cortex-A73大核跑2.2GHz加上两颗Cortex-A53小核跑1.8GHz，还带一个5.0 TOPS算力的NPU。这个配置在2019年的时候可是高端货，Khadas VIM3开发板用的就是它，当年一块板子就要上千块。现在这价格被腰斩到只剩个零头，感觉像是不把芯片当回事了。


![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/E9h3abOJCenR3I0NiceUUMSc5ObjKmU0Zn7ycymIJVjlgjth4cibGj6npiaoqia4ibOnptZ7J3EsgQ9oa83EPtTko4hicSMIjOPPzlBjH1YicLGviaA/640?wx_fmt=png)


再看扩展性，这台小盒子能塞三块2.5寸硬盘，千兆网口也齐了，做NAS或者软路由的底子算是有了。4G内存跑飞牛问题不大，毕竟飞牛最低只要2G内存就能跑。而且卖家已经把飞牛ARM版刷好了。


![图片](https://mmbiz.qpic.cn/mmbiz_png/E9h3abOJCemYdUwHXyEHrT745SjBwETL1XQ6IwDBR6l5GWCvekheicIWr0ibX5yTsE04qR97wncibAdnvMyh6wQ1DD9CKQ4XnnP0ZJ1cyGk8w8/640?wx_fmt=png)


不过这机器的真实出身你得心里有数。它本质上就是PCDN业务的淘汰设备，也就是之前用来跑闲置宽带的盒子。卖家说只跑了两三个月，机器很新，这倒是有可能的，毕竟现在运营商对PCDN打击越来越严，山东、河南、江苏等省份查得紧，很多挂机的被迫停机出货。


![图片](https://mmbiz.qpic.cn/mmbiz_png/E9h3abOJCenV4890PyN468xJAkkr0b0SbTTvouXBSLBlgQjicWScQcL0zg1wXxENGup1SBHBsxSiaKjElHj2nl1HNdOjUue4sVGNgt0YdXico4/640?wx_fmt=png)


但这个产品的短板你也得知道。4G内存够用但不富裕，想开十几个Docker容器肯定扛不住。8G存储装完系统就剩不了多少空间了，必须配硬盘才能当NAS用。而且ARM平台的软件生态和折腾资料相比x86要少一些，刷第三方系统、装Docker镜像的时候可能会遇到更多坑。


![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/E9h3abOJCelAGPRqLA8jh1zlGxc6nvgcPdb0oMkRribBEl6XrrFWiaVv6rzib7mmSJMejRM9zcl4gGMtvibyRz7ficuJEmGa0kSjXjzVafV1EW5A/640?wx_fmt=png)


如果你正好缺一台低功耗的下载机或者轻量NAS，这个价位能买到六核A311D加4G内存加飞牛，说实话挺香的。四核A53的斐讯N1都卖到80到130元了，你再加几十块钱就能拿到性能高出一截的机器，这买卖我觉得不亏。


![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/E9h3abOJCelPqnib6j5MKTDPdTGUUIheLu4v2SuUibBJPIswh2kL4voeBTxsWg9OAjs6NZjlV0HZRtMia2NyrqrMHgzOk2aQdc0K0XG4jkEuOs/640?wx_fmt=png)


你觉得这台159元的OES值不值得入手？是拿它当家庭NAS，还是跑软路由，或者干脆刷个安卓系统当电视盒子用？留言区聊聊你的看法。
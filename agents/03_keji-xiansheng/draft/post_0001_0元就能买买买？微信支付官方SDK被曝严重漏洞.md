# 0元就能买买买？微信支付官方SDK被曝严重漏洞

![封面图](http://mmbiz.qpic.cn/mmbiz_jpg/P3SqL3Qw4YibHz3o1uBb8TLDf0y4ax3iaHkBdYI3iaymtNMAKKauHM2N9NCLN3cY0LaNNxibW132hYOQXTGZInnuzQ/0?wx_fmt=jpeg)

> 原文链接：https://mp.weixin.qq.com/s/W3L3SClHVqe7kpk10Cus2w

![图片](https://mmbiz.qpic.cn/mmbiz_gif/P3SqL3Qw4YibTH6HfT3Nz0CialmxoGMzibX9mGBicmAKqfXL3FvxGzDwUFy6Nrb90PVT4ds3TSSPYbEVgcaKIRR0aQ/640?wx_fmt=gif)


![图片](https://mmbiz.qpic.cn/mmbiz_png/P3SqL3Qw4YicAvGuh4oJa8BMYZqb5IY5Yy1FUUywfjRgwUtfcUmuvYPjDYl0WRkdsJM0FSiboBZ7HDYBp5rGEiaqg/640?wx_fmt=png)


科技先生科技主题的极客新闻和社区，有趣，有料！

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/P3SqL3Qw4YicAvGuh4oJa8BMYZqb5IY5Y4ugMEYGMRSmYbArdeaGp8pCQicfswkGUjicmO1uZpbsczEib0IIzr8Dzw/640?wx_fmt=jpeg)


———— / BEGIN / ————


![图片](https://mmbiz.qpic.cn/mmbiz_jpg/P3SqL3Qw4YibHz3o1uBb8TLDf0y4ax3iaHdfialZUF4jfVwSMDJeoRa1pj2NqX5ONqLMoRygK0aiaXejVfS9NIb92w/640?wx_fmt=jpeg)


　　今日，白帽汇安全研究院关注到国外安全社区公布微信支付官方SDK存在严重漏洞，可导致商家服务器被入侵(绕过支付的效果)。目前，漏洞详细信息以及攻击方式已被公开，影响范围巨大(已确认陌陌、vivo因使用该SDK而存在该漏洞)，建议用到JAVA SDK的商户快速检查并修复。


　　目前，确认该漏洞(XXE漏洞)影响JAVA版本的SDK，历史上曾经也出现过PHP版本SDK存在同样的漏洞。**截止目前，白帽汇安全研究院发现，微信官方共两次修复该漏洞，两处修改时间分别为2018年07月03日12时47分和2018年07月04日8时09分。分别修复了XXE漏洞和可DoS(导致拒绝服务)攻击的漏洞。**提醒广场商户发现检测是否最新代码，及时更新修复漏洞。


![图片](https://mmbiz.qpic.cn/mmbiz_png/P3SqL3Qw4YibHz3o1uBb8TLDf0y4ax3iaHHeFLic48Hdb4UbVz2gMlYpoNahianicNIsLUoGbCNTicHdErULrblqSyRA/640?wx_fmt=png)


代码修改时间变化表


![图片](https://mmbiz.qpic.cn/mmbiz_png/P3SqL3Qw4YibHz3o1uBb8TLDf0y4ax3iaHn4u8xAoFiboqMD3Pq8GKKXXPmptv4RIvAVSvBFPJoVsXDyDvLvBJxsQ/640?wx_fmt=png)


　　原始版本与最新版本更新代码的差异


　　**什么是XML外部实体注入(XML External Entity，简称XXE)?**


　　当允许引用外部实体时，通过构造恶意内容，可导致读取任意文件、执行系统命令、探测内网端口、攻击内网网站等危害。


**漏洞影响**


　　此次漏洞可使攻击者向通知URL 构建恶意有效payload，以便根据需要窃取商家服务器的任何信息。一旦攻击者获得商家的关键安全密钥(md5-key和merchant-Id等)，他甚至可以通过发送伪造信息来欺骗商家而无需付费购买任何东西。目前微信官方尚未对SDK进行修复。现已有momo、vivo已经验证被该漏洞影响。微信支付被广泛应用于各种支付场景。**目前，该白帽子在没有通知厂商的情况就对外公布，至此，官方还没有发布相关补丁。提醒广大厂商检查自己的系统，及时进行修复，防止带来损失。**


　　截止2018年07月03日16时，微信官方还并未发布相关补丁。


![图片](https://mmbiz.qpic.cn/mmbiz_png/P3SqL3Qw4YibHz3o1uBb8TLDf0y4ax3iaHcdyOW7iaeFjKjzosM00Fd1Q284Ek8M52gziaEBUbeYNicMBzia5aV8LjKg/640?wx_fmt=png)


漏洞利用


![图片](https://mmbiz.qpic.cn/mmbiz_png/P3SqL3Qw4YibHz3o1uBb8TLDf0y4ax3iaHiaKVPKV0woC9FQ6B7txqnwarmGrX30okP9m21SBuBPjUHibfDeFGo4gA/640?wx_fmt=png)


![图片](https://mmbiz.qpic.cn/mmbiz_png/P3SqL3Qw4YibHz3o1uBb8TLDf0y4ax3iaHQiaRmE3ibXTKwaJ0wkCv1OicPmBUL5UAdJSk8r43cCI9hFBNjh2kRMD2A/640?wx_fmt=png)


**漏洞复现**　　


　　目前，白帽汇安全研究院已经通过本地复现此漏洞，漏洞真实存在。我们通过Burpsuite做简单测试，可以看到服务器已成功请求我们的远程服务器。这里还可进一步获取服务器中数据，甚至执行系统命令，提升系统权限。


![图片](https://mmbiz.qpic.cn/mmbiz_png/P3SqL3Qw4YibHz3o1uBb8TLDf0y4ax3iaHV80ayfaX8mWZayplnUoQzZgHJKh8OnIKRp1EMGVibGBEfVooVHuFmEg/640?wx_fmt=png)


　　以下为使用微信支付JAVA SDK所构造的漏洞代码，只要使用WXPayUtil.xmlToMap方法，且传入的数据可控，就会造成该漏洞。漏洞示例代码如下：


![图片](https://mmbiz.qpic.cn/mmbiz_png/P3SqL3Qw4YibHz3o1uBb8TLDf0y4ax3iaHSlovfPPBSNr7oQ1D00SUGe0R9lmyF3ejZs7la6c4iauyZznoMemlVPw/640?wx_fmt=png)


**修复建议**


　　用户可使用开发语言提供的禁用外部实体的方法。java禁用外部实体的代码如下： DocumentBuilderFactory dbf =DocumentBuilderFactory.newInstance(); dbf.setExpandEntityReferences(false);


　　补充：


　　根据发布国外发布的内容，猜测漏洞报告者可能是中国人。在其发布的内容中明确使用了中文的标点符号。


![图片](https://mmbiz.qpic.cn/mmbiz_png/P3SqL3Qw4YibHz3o1uBb8TLDf0y4ax3iaHojj3lGBn17jUR0V0SnnRmWYnFEYZ3mTDa6PSGeL7q6Jrgbnibmib32ew/640?wx_fmt=png)


 ———— / END / ————


![图片](https://mmbiz.qpic.cn/mmbiz_png/P3SqL3Qw4YibTH6HfT3Nz0CialmxoGMzibXa8hy4bWGGlUElc6O28ricI1u3ibFsibUPibNEQ17uN0a8M7YVMtPczoniaw/640?wx_fmt=png)
通义千问-图像编辑模型支持多图输入和多图输出，可精确修改图内文字、增删或移动物体、改变主体动作、迁移图片风格及增强画面细节。

快速开始
本示例将演示如何使用qwen-image-edit-max模型，根据3张输入图像和提示词，生成2张编辑后的图像。

输入提示词：图1中的女生穿着图2中的黑色裙子按图3的姿势坐下。




输入图像1

输入图像2

输入图像3

输出图像（多张图像）

image99

image98

image89

image100

imageout2

在调用前，您需要获取API Key，再配置API Key到环境变量。

如需通过SDK进行调用，请安装DashScope SDK。目前，该SDK已支持Python和Java。

通义千问-图像编辑模型系列模型均支持传入 1-3 张图像。其中，qwen-image-edit-max和qwen-image-edit-plus系列模型支持生成 1-6 张图像，qwen-image-edit 模型仅支持生成1张图像。生成的图像URL链接有效期为24小时，请及时通过URL下载图像到本地。

PythonJavacurl
 
import json
import os
from dashscope import MultiModalConversation
import dashscope

# 以下为中国（北京）地域url，若使用新加坡地域的模型，需将url替换为：https://dashscope-intl.aliyuncs.com/api/v1
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

# 模型支持输入1-3张图片
messages = [
    {
        "role": "user",
        "content": [
            {"image": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250925/thtclx/input1.png"},
            {"image": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250925/iclsnx/input2.png"},
            {"image": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250925/gborgw/input3.png"},
            {"text": "图1中的女生穿着图2中的黑色裙子按图3的姿势坐下"}
        ]
    }
]

# 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
# 若没有配置环境变量，请用百炼 API Key 将下行替换为：api_key="sk-xxx"
api_key = os.getenv("DASHSCOPE_API_KEY")

# qwen-image-edit-max、qwen-image-edit-plus系列支持输出1-6张图片，此处以2张为例
response = MultiModalConversation.call(
    api_key=api_key,
    model="qwen-image-edit-max",
    messages=messages,
    stream=False,
    n=2,
    watermark=False,
    negative_prompt=" ",
    prompt_extend=True,
    size="1024*1536",
)

if response.status_code == 200:
    # 如需查看完整响应，请取消下行注释
    # print(json.dumps(response, ensure_ascii=False))
    for i, content in enumerate(response.output.choices[0].message.content):
        print(f"输出图像{i+1}的URL:{content['image']}")
else:
    print(f"HTTP返回码：{response.status_code}")
    print(f"错误码：{response.code}")
    print(f"错误信息：{response.message}")
    print("请参考文档：https://help.aliyun.com/zh/model-studio/error-code")
响应示例

通过URL下载图像到本地

模型选型建议
qwen-image-edit-max 系列：旗舰级图像编辑模型，具备更稳定、丰富的编辑能力，推荐在对编辑质量有高要求的场景中使用。

qwen-image-edit-plus 系列：提供强大的通用编辑能力，在文本编辑、工业设计、几何推理及角色一致性方面表现突出。

qwen-image-edit不支持多图输出、调整输出图像分辨率和提示词智能优化等功能，推荐替换为qwen-image-edit-plus模型。
各地域支持的模型请参见模型列表。

输入说明
输入图像（messages）
messages 是一个数组，且必须仅包含一个对象。该对象需包含 role 和 content 属性。其中role必须设置为user，content需要同时包含image（1-3张图像）和text（一条编辑指令）。

输入图片必须满足以下要求：

图片格式：JPG、JPEG、PNG、BMP、TIFF、WEBP和GIF。

输出图像为PNG格式，对于GIF动图，仅处理其第一帧。
图片分辨率：为获得最佳效果，建议图像的宽和高均在384像素至3072像素之间。分辨率过低可能导致生成效果模糊，过高则会增加处理时长。

文件大小：单张图片文件大小不得超过 10MB。

 
"messages": [
    {
        "role": "user",
        "content": [
            { "image": "图1的公网URL或Base64数据" },
            { "image": "图2的公网URL或Base64数据" },
            { "image": "图3的公网URL或Base64数据" },
            { "text": "您的编辑指令，例如：'图1中的女生穿着图2中的黑色裙子按图3的姿势坐下'" }
        ]
    }
]
图像输入顺序
多图输入时，按照数组顺序定义图像顺序，编辑指令需要与 content 中的图像顺序对应（如“图1”、“图2”）。




输入图像1

输入图像2

输出图像

image95

image96

5

将图1中女生的衣服替换为图2中女生的衣服

4

将图2中女生的衣服替换为图1中女生的衣服

图像传入方式
公网URL

提供一个公网可访问的图像地址，支持 HTTP 或 HTTPS 协议。本地文件请参见上传文件获取临时URL。

示例值：https://xxxx/img.png。

Base64编码

将图像文件转换为 Base64 编码字符串，并按格式拼接：data:{mime_type};base64,{base64_data}。

{mime_type}：图像的媒体类型，需与文件格式对应。

{base64_data}：文件经过 Base64 编码后的字符串。

示例值：data:image/jpeg;base64,GDU7MtCZz...（示例已截断，仅做演示）

完整示例代码请参见Python SDK调用、Java SDK调用。

更多参数
可以通过以下可选参数调整生成效果：

n：指定输出图像数量，默认值为1。qwen-image-edit-max和qwen-image-edit-plus系列模型支持输出1-6张图片，qwen-image-edit模型仅支持输出1张图片。

negative_prompt（反向提示词）：描述不希望在画面中出现的内容，如“模糊”、“多余的手指”等，用于辅助优化生成质量。

watermark：是否在图像右下角添加 "Qwen-Image" 水印。默认值为 false。水印样式如下：

1

seed：随机数种子。取值范围是[0, 2147483647]。如果不提供，则算法自动生成一个随机数作为种子。使用相同的 seed 值可帮助生成内容保持相对稳定。

以下可选参数仅qwen-image-edit-max、qwen-image-edit-plus系列模型支持：

size：设置输出图像的分辨率，格式为宽*高，例如"1024*2048"，宽和高的取值范围均为[512, 2048]像素。若不设置，输出图像将保持与原图（多图输入时为最后一张图）相似的长宽比，总像素接近1024*1024分辨率。

prompt_extend：是否开启prompt智能改写功能，默认值为 true。开启后，模型将优化提示词，对描述性不足、较为简单的prompt提升效果较明显。

完整参数列表请参考通义千问-图像编辑API。

效果概览
多图融合




输入图像1

输入图像2

输入图像3

输出图像

image83

image103

1

2

图1中的女生戴着图2中的项链，左肩挎着图3中的包

主体一致性保持




输入图像

输出图像1

输出图像2

输出图像3

image5

image4

修改为蓝底证件照，人物穿上白色衬衫，黑色西装，打着条纹领带

image6

人物穿上白色衬衫，灰色西装，打着条纹领带，一只手摸着领带，浅色背景

image7

人物穿着粗笔刷字体的“千问图像”的黑色卫衣，依靠在护栏边，阳光照在发丝上，身后是大桥和海

image12

image13

把这个空调放在客厅，沙发旁边

image14

在空调出风口增加雾气，一直到沙发上，并且增加绿叶。

image15

在上方增加白色的手写体"自然新风 畅享呼吸"

草图创作


输入图像

输出图像

image42

image43

生成一张图像，符合图1所勾勒出的精致形状，并遵循以下描述：一位年轻的女子在阳光明媚的日子里微笑着，她戴着一副棕色的圆形太阳镜，镜框上有豹纹图案。她的头发被整齐地盘起，耳朵上佩戴着珍珠耳环，脖子上围着一条带有紫色星星图案的深蓝色围巾，穿着一件黑色皮夹克。

image44

生成一张图像，符合图1所勾勒出的精致形状，并遵循以下描述：一位年老的老人朝着镜头微笑，他的脸上布满皱纹，头发在风中凌乱，戴着一副圆框的老花镜。脖子上戴着一条破旧的红色围巾，上面有星星图案。穿着一件棉衣。

文创生成


输入图像

输出图像

图片 1

image23

让这只熊坐在月亮下（用白色背景上的浅灰弯月轮廓表示），抱着吉他，周围漂浮着小星星和诗句气泡，如“Be Kind”。

image22

将这个图案印在一件T恤和一个手提纸袋上。一个女模特正在展示这些物品。这个女生还戴着一顶鸭舌帽，帽子上写着"Be kind”。

image21

一个超逼真的1/7比例角色模型，设计为商业产品成品，放置在一台带有白色键盘的iMac电脑桌上。模型站在一个干净、圆形的透明亚克力底座上，没有标签或文字。专业的摄影棚灯光凸显了雕刻细节。在背景的iMac屏幕上，展示同一模型的ZBrush建模过程。在模型旁边，放置一个包装盒，前面带有透明窗户，仅显示内部透明塑料壳，其高度略高于模型，尺寸合理以容纳模型。

image

这只熊穿着宇航服，伸出手指向远方

image

这只熊穿着华丽的舞裙，双臂展开，做出优雅的舞蹈动作

image

这只熊穿着运动服，手里拿着篮球，单腿弯曲

根据深度图生成图像


输入图像

输出图像

image36

image37

生成一张图像，符合图1所勾勒出的深度图，并遵循以下描述：在一条街边的小巷中停放着一辆蓝色的自行车，背景中有几株从石缝中长出来的杂草

image38

生成一张图像，符合图1所勾勒出的深度图，并遵循以下描述：一辆红色的破旧的自行车停在一条泥泞的小路上，背景是茂密的原始森林

根据关键点生成图像


输入图像

输出图像

image40

image41

生成一张图像，符合图1所勾勒出的人体姿态，并遵循以下描述：一位身穿着汉服的中国美女，在雨中撑着油纸伞，背景是苏州园林。

image39

生成一张图像，符合图1所勾勒出的人体姿态，并遵循以下描述：一位男生，站在地铁站台上，他头上戴着一顶棒球帽，穿着T恤和牛仔裤。背后是飞驰而过的列车。

文字编辑




输入图像

输出图像

输入图像

输出图像

image

image

将拼字游戏方块上'HEALTH INSURANCE’ 替换为'明天会更好'

image

image

将便条上的短语“Take a Breather”更改为“Relax and Recharge”



输入图像

输出图像

image53

image45

将“Qwen-Image”换成黑色的滴墨字体

image46

将“Qwen-Image”换成黑色的手写字体

image49

将“Qwen-Image”换成黑色的像素字体

image54

将“Qwen-Image”换成红色

image57

将“Qwen-Image”换成蓝紫渐变色

image59

将“Qwen-Image”换成糖果色

image63

将“Qwen-Image”材质换成金属

image64

将“Qwen-Image”材质换成云朵

image67

将“Qwen-Image”材质换成玻璃

增删改及替换



能力

输入图像

输出图像

新增元素

image

image

在企鹅前方添加一个小型木制标牌，上面写着“Welcome to Penguin Beach”。

删除元素

image

image

删除餐盘上的头发

替换元素

image

image

把桃子变成苹果

人像修改

image

image

让她闭上眼睛

姿态修改

image8

image9

她举起双手，手掌朝向镜头，手指张开，做出一个俏皮的姿势

视角转换




输入图像

输出图像

输入图像

输出图像

image

image

获得正视视角

image

image

朝向左侧

image

image

获得后侧视角

image

image

朝向右侧

背景替换


输入图像

输出图像

image

image

将背景更改为海滩

image

将原图背景替换为真实的现代教室场景，背景中央为一块深绿色或墨黑色的传统黑板，黑板表面用白色粉笔工整地写着中文“通义千问”

老照片处理



能力

输入图像

输出图像

老照片修复及上色

image

image

修复老照片，去除划痕，降低噪点，增强细节，高分辨率，画面真实，肤色自然，面部特征清晰，无变形。

image31

image32

根据内容智能上色，使图像更生动

计费与限流
模型免费额度和计费单价请参见模型列表与价格。

模型限流请参见通义千问（Qwen-Image）。

计费说明：

按成功生成的 图像张数 计费。模型调用失败或处理错误不产生任何费用，也不消耗免费额度。

您可开启“免费额度用完即停”功能，以避免免费额度耗尽后产生额外费用。详情请参见免费额度。

API参考
API的输入输出参数，请参见通义千问-图像编辑。

错误码
如果模型调用失败并返回报错信息，请参见错误信息进行解决。

常见问题
Q：通义千问图像编辑模型支持哪些语言？
A：目前正式支持简体中文和英文；其他语言可自行尝试，但效果存在不确定性。

Q：上传多张不同比例的参考图时，输出图像的比例以哪张为准？
A：默认情况下，输出图像会以最后一张上传的参考图的比例为准。您也可以通过设置 parameters.size 参数来自定义输出图像的尺寸。

Q：如何查看模型调用量？
A：模型的调用信息存在小时级延迟，在模型调用完一小时后，请在模型观测（北京或新加坡）页面，查看调用量、调用次数、成功率等指标。详情请参见账单查询与成本管理。

更多问题请参见图像生成常见问题。
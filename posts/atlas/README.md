# 山河之间 · 个人地理志

公开页面：<https://ha2fde.github.io/posts/atlas/>

独立静态页面，无构建步骤、第三方脚本、地图 API Key 或后台服务。
GitHub Pages 直接提供文件即可。博客首页已添加入口。

打开页面直接进入省域地图和地区切换，不显示封面、开场介绍或重复的旅途概览。

## 内容

- 2025 年十月：甘肃 / 河西走廊，10 张本人此前公开的照片。
- 2026 年十月：山西，9 张本人此前公开的照片。
- 真实省界上的地点选择、地图与相册同步、可用键盘与触摸操作的大图浏览。
- 地理文化背景与照片对应地点的资料链接。

甘肃 10 张照片的地点已由本人确认，均有地图索引：兰州、武威鸠摩罗什寺、
天梯山石窟、乌鞘岭、张掖七彩丹霞、平山湖大峡谷、嘉峪关关城、
鸣沙山月牙泉、莫高窟、锁阳城旁的塔尔寺遗址。

山西相册中的双塔为双塔公园内的永祚寺（双塔寺）；山中楼阁为
天龙山石窟第9窟外的漫山阁；水边照片为汾河景区的雁丘园，
与元好问《摸鱼儿·雁丘词》有关。三处均已由本人确认，并加入地图索引。

两组照片的地点均已确认。不根据文件名、旅行计划或视觉猜测补造定位。
地图连线是地点索引，不是行车轨迹；
页面不声称展示完整行程。公开照片不含 EXIF。

旅行页以地理、文化与影像为主，不使用个人名字，不设个人介绍段落。

## 维护

`data.js` 包含相册文字、地图点位及文化资料链接。新增照片时添加记录，
设置 `trip`、`id`、`width`、`height`、`title`、`subtitle` 和描述性 `alt`；
确认地点后可设置 `place` 并补充地图点。原图放在 `photos/`，沿用 WebP，
避免上传大文件、带 GPS 的相机原件或私人行程凭据。

`maps.js` 为省界数据，`main.js` 负责地图投影与交互，`style.css` 负责响应式布局。
更换地区时更新边界、点位及 HTML 中对应入口、统计和说明。

## 资料来源

- [阿里云 DataV GeoAtlas](https://datav.aliyun.com/portal/school/atlas/area_selector)
  - 甘肃：<https://geo.datav.aliyun.com/areas_v3/bound/620000.json>
  - 山西：<https://geo.datav.aliyun.com/areas_v3/bound/140000.json>
  - 获取日期：2026-11-05；以本地纬度校正等距投影展示，仅作个人旅行地理示意。
- [国家林业和草原局：走进秘境祁连山](https://www.forestry.gov.cn/c/www/mlzgxczrbhd/149760.jhtml)
- UNESCO：[莫高窟](https://whc.unesco.org/en/list/440/)、[云冈石窟](https://whc.unesco.org/en/list/1039/)、[五台山](https://whc.unesco.org/en/list/1279/)。
- [人民日报海外版：跟着元好问访雁丘](https://paper.people.com.cn/hwbwap/html/2024-01/15/content_26037111.htm)。

## 发布前检查

1. `node --check main.js`、`node --check data.js`、`node --check maps.js`。
2. 检查图片及所有本地引用存在，且没有 `/lab/` 链接或私人数据。
3. 桌面与手机查看两个地图、地点切换和完整相册。
4. 验证大图关闭、左右切换、键盘、焦点恢复与手机无横向溢出。

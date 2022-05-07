# GAN

## Inroduction

[Generative adversial nets](https://arxiv.org/abs/1406.2661) was published in 2014 NIPSd

[DCGAN](https://arxiv.org/pdf/1511.06434.pdf) which using CNN in GAN has made a huge improvement.

TODO: an online website

## Relevant reference

project:

- [Github-GAN+DCGAN+WGAN-pytorch](https://github.com/Zeleni9/pytorch-wgan) (easy to use,recommand)
- [Github-GAN*-pytorch](https://github.com/eriklindernoren/PyTorch-GAN) (overall)
- [Github-DCGAN-tensorflow](https://github.com/carpedm20/DCGAN-tensorflow)
- [Github-GAN*-tensorflow](https://github.com/YadiraF/GAN)

knowledge:

- [知乎-GAN学习指南：从原理入门到制作生成Demo](https://zhuanlan.zhihu.com/p/24767059)
- [GAN video by Li mu](https://www.bilibili.com/video/BV1rb4y187vD)
- [KL散度](https://zhuanlan.zhihu.com/p/365400000)

## Requirements

- python : 3
- pytorch
- other dependencies

  ```bash
  pip install -r requirements.txt
  ```

## Dataset(Anime)

![20220507024303](https://raw.githubusercontent.com/learner-lu/picbed/master/20220507024303.png)![20220507024427](https://raw.githubusercontent.com/learner-lu/picbed/master/20220507024427.png)

download the dataset zip and unzip it under `dataset` as `dataset/anime`

total dataset contains about 50000+ images of 96x96

- [Github-download](https://github.com/luzhixing12345/GAN/releases/download/v0.0.2/faces.zip)

  > try to use [Github proxy](https://ghproxy.com/) if too slow

## Use

### Train

```bash
python train.py
```

### Generate an anime picture

```bash
python generate.py
```

## Pretrained model

|D-epoch|download|G-epoch|download|
|:--:|:--:|:--:|:--:|
|D-500(best)|[download]()|G-500(best)|[download]()|

download the pretrained model D and G and move it under `./model`

> actually if you just want to generate an anime picture you only need to download G
>
> D could be used to discriminate whether the picture is real or not

- generate an anime picture

  ```bash
  python generate.py
  ```

- discriminate a picture

  ```bash
  python discriminate.py -i example-01-T.jpg
  ```

## Result

## Conclusion

## [Lab report]()

> actually this is my closing report of Data-science-introduction lesson, see more infomation in another [repository](https://github.com/luzhixing12345/data-science-introduction)

## Some questions you may ask and some problems you may encounter

1. How to train with my own dataset?

2. It seems to slow to train each epoch, anything help?

3. The result doesn't seem well...

## Some errors you may encounter

1. BrokenPipeError: [Errno 32] Broken pipe

   multiple threads in Windows, add `DATALOADER.NUM_WORKERS 0`

   ```bash
   python train.py --config_file configs/GAN.yaml DATALOADER.NUM_WORKERS 0
   ```

if you have any other question, leave your confusion in Issue and I will apply as soon as possible.

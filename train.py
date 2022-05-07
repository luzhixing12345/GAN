'''
*Copyright (c) 2022 All rights reserved
*@description: train GAN model
*@author: Zhixing Lu
*@date: 2022-05-06
*@email: luzhixing12345@163.com
*@Github: luzhixing12345
'''

import time
from config.config import get_cfg
from utils import *

def main():
    
    cfg = get_cfg()
    cfg = project_preprocess(cfg)

    train_dataloader, test_dataloader = preprare_dataloader(cfg)
    
    model = build_model(cfg)
    model.train(train_dataloader)
    

if __name__ == '__main__':
    main()

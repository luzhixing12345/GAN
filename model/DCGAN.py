import torch
import torch.nn as nn
from torch.autograd import Variable
import os
import time
from torchvision import utils
from model.BaseModule import BasicModel

# basic model structure comes from https://github.com/Zeleni9/pytorch-wgan

class Generator(torch.nn.Module):
    def __init__(self, channels):
        super().__init__()
        # Input_dim = 100
        # Output_dim = C (number of channels)
        self.main_module = nn.Sequential(
            
            # input is Z which size is (batch size x C x 1 X 1),going into a convolution
            # by default (32, 100, 1, 1)
            # project and reshape
            nn.ConvTranspose2d(in_channels=100, out_channels=1024, kernel_size=4, stride=1, padding=0),
            nn.BatchNorm2d(num_features=1024),
            nn.ReLU(True),

            # CONV1
            # State (1024x4x4)
            nn.ConvTranspose2d(in_channels=1024, out_channels=512, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(num_features=512),
            nn.ReLU(True),

            # CONV2
            # State (512x8x8)
            nn.ConvTranspose2d(in_channels=512, out_channels=256, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(num_features=256),
            nn.ReLU(True),
            
            # CONV3
            # State (256x16x16)
            nn.ConvTranspose2d(in_channels=256, out_channels=128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(num_features=128),
            nn.ReLU(True),
            
            # CONV4
            # State (128x32x32)
            nn.ConvTranspose2d(in_channels=128, out_channels=channels, kernel_size=4, stride=2, padding=1))
            # output of main module --> Image (batch size x C x 64 x 64)
            # default (32, 3, 64, 64)

        # output activation function is Tanh
        self.output = nn.Tanh()

    def forward(self, x):
        x = self.main_module(x)
        return self.output(x)


class Discriminator(torch.nn.Module):
    def __init__(self, channels):
        super().__init__()
        # Input_dim = channels (CxHxW)
        # Output_dim = 1
        self.main_module = nn.Sequential(
            # State (CxHxW)
            # default (32, 3, 64, 64)
            nn.Conv2d(in_channels=channels, out_channels=256, kernel_size=4, stride=2, padding=1),
            nn.LeakyReLU(0.2, inplace=True),

            # State (256x H/2 x W/2)
            nn.Conv2d(in_channels=256, out_channels=512, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2, inplace=True),

            # State (512x H/4 x W/4)
            nn.Conv2d(in_channels=512, out_channels=1024, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(1024),
            nn.LeakyReLU(0.2, inplace=True),
            
            # State (1024x H/8 x W/8)
            nn.Conv2d(in_channels=1024, out_channels=2048, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(2048),
            nn.LeakyReLU(0.2, inplace=True))
            # outptut of main module --> State (2048x H/8 x W/8)

        self.output = nn.Sequential(
            nn.Conv2d(in_channels=2048, out_channels=1, kernel_size=4, stride=1, padding=0),
            # Output 1
            nn.Sigmoid())
        
            # output size (1 x (H/16-3) x (W/16-3))
            # default (32, 1, 1, 1)

    def forward(self, x):
        x = self.main_module(x)
        return self.output(x)


class DCGAN(BasicModel):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.G = Generator(self.channels)
        self.D = Discriminator(self.channels)

        # binary cross entropy loss and optimizer
        self.loss = nn.BCELoss()

        # Using lower learning rate than suggested by (ADAM authors) lr=0.0002  and Beta_1 = 0.5 instead od 0.9 works better [Radford2015]
        self.d_optimizer = torch.optim.Adam(self.D.parameters(), lr=cfg.SOLVER.BASE_LR, betas=cfg.SOLVER.BETAS)
        self.g_optimizer = torch.optim.Adam(self.G.parameters(), lr=cfg.SOLVER.BASE_LR, betas=cfg.SOLVER.BETAS)


    def train(self, train_loader):
        
        start_time = time.time()
        generator_iter = 0

        for epoch in range(self.epochs):
            epoch_start_time = time.time()
            
            for i, images in enumerate(train_loader):
                # Check if round number of batches
                if i == train_loader.dataset.__len__() // self.batch_size:
                    break

                z = torch.rand((self.batch_size, 100, 1, 1))
                
                images = Variable(images).to(self.device)
                z = Variable(z).to(self.device)

                real_labels = Variable(torch.ones(self.batch_size)).to(self.device)
                fake_labels = Variable(torch.zeros(self.batch_size)).to(self.device)

                # Train discriminator
                # Compute BCE_Loss using real images
                outputs = self.D(images)
                d_loss_real = self.loss(outputs.flatten(), real_labels)

                # Compute BCE Loss using fake images
                z = Variable(torch.randn(self.batch_size, 100, 1, 1)).to(self.device)
                
                fake_images = self.G(z)
                outputs = self.D(fake_images)
                d_loss_fake = self.loss(outputs.flatten(), fake_labels)

                # Optimize discriminator
                d_loss = d_loss_real + d_loss_fake
                self.D.zero_grad()
                d_loss.backward()
                self.d_optimizer.step()

                # Train generator
                # Compute loss with fake images
                
                z = Variable(torch.randn(self.batch_size, 100, 1, 1)).to(self.device)
                
                fake_images = self.G(z)
                outputs = self.D(fake_images)
                g_loss = self.loss(outputs.flatten(), real_labels)

                # Optimize generator
                self.D.zero_grad()
                self.G.zero_grad()
                g_loss.backward()
                self.g_optimizer.step()
                generator_iter += 1

                if ((i + 1) % self.checkpoint_freq) == 0:
                    print("Epoch: [%2d] [%4d/%4d] D_loss: %.8f, G_loss: %.8f" %
                          ((epoch + 1), (i + 1), train_loader.dataset.__len__() // self.batch_size, d_loss.data, g_loss.data))

                    z = Variable(torch.randn(self.batch_size, 100, 1, 1)).to(self.device)

                    # log losses and save images
                    info = {
                        'd_loss': d_loss.data,
                        'g_loss': g_loss.data
                    }
                    self.logger.log_losses(info, generator_iter)

                    info = {
                        'real_images': self.reshape_images(images),
                        'generated_images': self.reshape_images(self.G(z))
                    }

                    self.logger.log_images(info, generator_iter)
                    self.save_model(epoch, generator_iter)
                    
                    
            end_epoch_time = time.time()
            print("Epoch time: %.2f" % (end_epoch_time - epoch_start_time))
        end_time = time.time()
        print("Total time: %.2f" % (end_time - start_time))
        # Save the trained parameters
        self.save_model(epoch, generator_iter)
        

    def generate_latent_walk(self, number):
        if not os.path.exists('interpolated_images/'):
            os.makedirs('interpolated_images/')

        # Interpolate between twe noise(z1, z2) with number_int steps between
        number_int = 10
        z_intp = torch.FloatTensor(1, 100, 1, 1)
        z1 = torch.randn(1, 100, 1, 1)
        z2 = torch.randn(1, 100, 1, 1)
        if self.cuda:
            z_intp = z_intp.cuda()
            z1 = z1.cuda()
            z2 = z2.cuda()

        z_intp = Variable(z_intp)
        images = []
        alpha = 1.0 / float(number_int + 1)
        print(alpha)
        for i in range(1, number_int + 1):
            z_intp.data = z1*alpha + z2*(1.0 - alpha)
            alpha += alpha
            fake_im = self.G(z_intp)
            fake_im = fake_im.mul(0.5).add(0.5) #denormalize
            images.append(fake_im.view(self.C,32,32).data.cpu())

        grid = utils.make_grid(images, nrow=number_int )
        utils.save_image(grid, 'interpolated_images/interpolated_{}.png'.format(str(number).zfill(3)))
        print("Saved interpolated images to interpolated_images/interpolated_{}.".format(str(number).zfill(3)))
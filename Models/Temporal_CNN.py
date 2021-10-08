import torch
import torch.nn as nn
import torch.nn.functional as F


class Temporal_CNN(nn.Module):
    def __init__(self, N_Classes: int, include_top = True ):
        super(Temporal_CNN, self).__init__()
        self.include_top = include_top
        self.conv1 = nn.Conv2d(in_channels=18, out_channels=96, kernel_size=(7, 7), stride=(2, 2))
        self.bn1 = nn.BatchNorm2d(96)
        self.pool1 = nn.MaxPool2d(kernel_size=(2, 2))

        self.conv2 = nn.Conv2d(in_channels=96, out_channels=256, kernel_size=(5, 5), stride=(2, 2))
        self.bn2 = nn.BatchNorm2d(256)
        self.pool2 = nn.MaxPool2d(kernel_size=(2, 2))

        self.conv3 = nn.Conv2d(in_channels=256, out_channels=512, kernel_size=(3, 3), stride=(1, 1))
        self.bn3 = nn.BatchNorm2d(512)

        self.conv4 = nn.Conv2d(in_channels=512, out_channels=512, kernel_size=(3, 3), stride=(1, 1))
        self.bn4 = nn.BatchNorm2d(512)

        self.conv5 = nn.Conv2d(in_channels=512, out_channels=512, kernel_size=(3, 3), stride=(1, 1))
        self.bn5 = nn.BatchNorm2d(512)
        self.pool5 = nn.MaxPool2d(kernel_size=(2, 2))

        self.flatten = nn.Flatten()

        self.lin6 = nn.Linear(in_features=4608, out_features=4096)
        self.drop6 = nn.Dropout(0.9)

        self.lin7 = nn.Linear(in_features=4096, out_features=2048)
        self.drop7 = nn.Dropout(0.9)

        self.lin8 = nn.Linear(in_features=2048, out_features=N_CLASSES)


    def forward(self, input):
        # input_shape must be (N, 18, 216, 216) -> (B, C, H, W)
        x = self.conv1(input)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.pool1(x)

        x = self.conv2(x)
        x = self.bn2(x)
        x = F.relu(x)
        x = self.pool2(x)

        x = self.conv3(x)
        x = self.bn3(x)
        x = F.relu(x)

        x = self.conv4(x)
        x = self.bn4(x)
        x = F.relu(x)

        x = self.conv5(x)
        x = self.bn5(x)
        x = F.relu(x)
        x = self.pool5(x)

        x = self.flatten(x)

        x = self.lin6(x)
        x = self.drop6(x)

        x = self.lin7(x)
        x = self.drop7(x)

        if self.include_top:
            x = self.lin8(x)
            x = F.softmax(x, dim=1)

        return x





if __name__ == '__main__':
    input_shape = (10, 18, 216, 216 ) # (B, C, H, W)
    N_CLASSES = 101
    inp = torch.rand(input_shape)
    model = Temporal_CNN(N_CLASSES)
    op = model(inp)
    print(op.shape)


# def temporal_CNN(input_shape, classes, weights_dir, include_top=True):
#     '''
#     The CNN for optical flow input.
#     Since optical flow is not a common image, we cannot finetune pre-trained ResNet (The weights trained on imagenet is
#     for images and thus is meaningless for optical flow)
#     :param input_shape: the shape of optical flow input
#     :param classes: number of classes
#     :return:
#     '''
#     optical_flow_input = Input(shape=input_shape)
#
#     x = Convolution2D(96, kernel_size=(7, 7), strides=(2, 2), padding='same', name='tmp_conv1')(optical_flow_input)
#     x = BatchNormalization(axis=3)(x)
#     x = Activation('relu')(x)
#     x = MaxPooling2D(pool_size=(2, 2))(x)
#
#     x = Convolution2D(256, kernel_size=(5, 5), strides=(2, 2), padding='same', name='tmp_conv2')(x)
#     x = BatchNormalization(axis=3)(x)
#     x = Activation('relu')(x)
#     x = MaxPooling2D(pool_size=(2, 2))(x)
#
#     x = Convolution2D(512, kernel_size=(3, 3), strides=(1, 1), padding='same', name='tmp_conv3')(x)
#     x = BatchNormalization(axis=3)(x)
#     x = Activation('relu')(x)
#
#     x = Convolution2D(512, kernel_size=(3, 3), strides=(1, 1), padding='same', name='tmp_conv4')(x)
#     x = BatchNormalization(axis=3)(x)
#     x = Activation('relu')(x)
#
#     x = Convolution2D(512, kernel_size=(3, 3), strides=(1, 1), padding='same', name='tmp_conv5')(x)
#     x = BatchNormalization(axis=3)(x)
#     x = Activation('relu')(x)
#     x = MaxPooling2D(pool_size=(2, 2))(x)
#
#     x = Flatten()(x)
#     x = Dense(4096, activation='relu', name='tmp_fc6')(x)
#     x = Dropout(0.9)(x)
#
#     x = Dense(2048, activation='relu', name='tmp_fc7')(x)
#     x = Dropout(0.9)(x)
#
#     if include_top:
#         x = Dense(classes, activation='softmax', name='tmp_fc101')(x)
#
#     model = Model(inputs=optical_flow_input, outputs=x, name='temporal_CNN')
#
#     if os.path.exists(weights_dir):
#         model.load_weights(weights_dir, by_name=True)
#
#     return model
#
#
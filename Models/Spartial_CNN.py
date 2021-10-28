import torch
import torch.nn as nn
import torchvision
import torch.nn.functional as F

# Repository to download the pretrained models from
# repo = "pytorch/vision"

class Spartial_CNN(nn.Module):
    def __init__(self, N_Classes ):
        super(Spartial_CNN, self).__init__()
        # use resnet50 pretrained on imagenet as our base model
        self.model = torchvision.models.resnet50(pretrained=True)

        # freeze pretrained layer
        for layer in self.model.parameters():
            layer.requires_grad = False

        # Custom layers for our model
        custom_head = nn.Sequential(
            nn.Linear(in_features=2048, out_features=2048),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),

            nn.Linear(in_features=2048, out_features=1024),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(in_features=1024, out_features=N_Classes),
        )

        # replace the last FC layer from resnet with out custom head
        self.model.fc = custom_head

    def forward(self, input):

        x = self.model(input)

        return F.softmax(x, dim=1)


if __name__ == '__main__':
    input_shape = (10, 3, 216, 216 ) # (B, C, H, W)
    N_CLASSES = 101
    inp = torch.rand(input_shape)
    model = Spartial_CNN(N_CLASSES)
    op = model(inp)
    print("Spartial Model")
    print(op.shape)

# def finetuned_resnet(include_top, weights_dir):
#     '''
#     :param include_top: True for training, False for generating intermediate results for
#                         LSTM cell
#     :param weights_dir: path to load finetune_resnet.h5
#     :return:
#     '''
#     base_model = ResNet50(include_top=False, weights='imagenet', input_shape=IMSIZE)
#     for layer in base_model.layers:
#         layer.trainable = False
#
#     x = base_model.output
#     x = Flatten()(x)
#     x = Dense(2048, activation='relu')(x)
#     x = Dropout(0.5)(x)
#     x = Dense(1024, activation='relu')(x)
#     x = Dropout(0.5)(x)
#
#     if include_top:
#         x = Dense(N_CLASSES, activation='softmax')(x)
#
#     model = Model(inputs=base_model.input, outputs=x)
#     if os.path.exists(weights_dir):
#         model.load_weights(weights_dir, by_name=True)
#
#     return model
#
#
# if __name__ == '__main__':
#     model = finetuned_resnet(include_top=True, weights_dir='')
#     print(model.summary())

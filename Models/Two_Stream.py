import torch
import torch.nn as nn
import torchvision
import torch.nn.functional as F
from Spatial_CNN import Spatial_CNN
from Temporal_CNN import Temporal_CNN


class Two_Stream(nn.Module):
    def __init__(self, N_Classes, spatial_weights=None, temporal_weights=None):
        super(Two_Stream, self).__init__()

        self.spatial_stream = Spatial_CNN(N_Classes)
        self.temporal_stream = Temporal_CNN(N_Classes)

        if spatial_weights is not None:
            # TODO: check it exception and path safety
            self.spatial_stream.load_state_dict(torch.load(spatial_weights))

        if temporal_weights is not None:
            # TODO: check it exception and path safety os.path exist
            self.temporal_stream.load_state_dict(torch.load(temporal_weights))

        # freeze all weights, the two models have been trained separately
        for layer in self.spatial_stream.parameters():
            layer.requires_grad = False

        for layer in self.temporal_stream.parameters():
            layer.requires_grad = False

    def forward(self, x, y):
        # x - input to spatial stream (B, 3, 216, 216)
        # y - input to temporal stream (B, 18, 216, 216)

        x = self.spatial_stream(x)
        y = self.temporal_stream(y)

        # Average
        x = torch.cat((x, y), dim=0).mean(dim=0)

        return x


if __name__ == "__main__":
    a  = torch.rand((1, 10))
    b  = torch.rand((1, 10))
    print(a)
    print(b)
    c = torch.cat([a, b], dim=0)
    print(c)

    print(c.mean(dim=0))

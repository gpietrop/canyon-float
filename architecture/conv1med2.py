from torch import nn

in_channels = 7
out_channels = 1


class Conv1dMed(nn.Module):
    def __init__(self):
        super(Conv1dMed, self).__init__()

        self.conv1 = nn.Conv1d(in_channels, 64, kernel_size=2, stride=1, padding=2)
        self.bn1 = nn.BatchNorm1d(64)
        self.af1 = nn.SELU()

        self.conv2 = nn.Conv1d(64, 128, kernel_size=2, stride=2, padding=1)
        self.bn2 = nn.BatchNorm1d(128)
        self.af2 = nn.SELU()

        self.conv3 = nn.Conv1d(128, 128, kernel_size=4, stride=1, padding=1)
        self.bn3 = nn.BatchNorm1d(128)
        self.af3 = nn.SELU()

        self.conv12 = nn.Conv1d(128, 128, kernel_size=4, stride=1, padding=2)
        self.bn12 = nn.BatchNorm1d(128)
        self.af12 = nn.SELU()

        self.deconv13 = nn.ConvTranspose1d(128, 128, kernel_size=2, stride=2, padding=2)
        self.bn13 = nn.BatchNorm1d(128)
        self.af13 = nn.SELU()

        self.conv14 = nn.Conv1d(128, 128, kernel_size=3, stride=1, padding=1)
        self.bn14 = nn.BatchNorm1d(128)
        self.af14 = nn.SELU()

        self.deconv15 = nn.ConvTranspose1d(128, 64, kernel_size=2, stride=2, padding=1)
        self.bn15 = nn.BatchNorm1d(64)
        self.af15 = nn.SELU()

        self.conv16 = nn.Conv1d(64, 32, kernel_size=2, stride=2, padding=1)
        self.bn16 = nn.BatchNorm1d(32)
        self.af16 = nn.SELU()

        self.conv17 = nn.Conv1d(32, out_channels, kernel_size=3, stride=1, padding=1)
        self.af17 = nn.SELU()

    def forward(self, x):
        x = self.bn1(self.af1(self.conv1(x)))
        x = self.bn2(self.af2(self.conv2(x)))
        x = self.bn3(self.af3(self.conv3(x)))
        x = self.bn12(self.af12(self.conv12(x)))
        x = self.bn13(self.af13(self.deconv13(x)))
        x = self.bn14(self.af14(self.conv14(x)))
        x = self.bn15(self.af15(self.deconv15(x)))
        x = self.bn16(self.af16(self.conv16(x)))
        x = self.af17(self.conv17(x))

        return x



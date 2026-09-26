import torch
import torch.nn as nn

class VegHealthCNN(nn.Module):
    """
    Lightweight 1D-Convolutional Neural Network for spectral-temporal crop health mapping.
    Total Parameters: 57,091
    Input Shape: (Batch_Size, 14, 1) or (Batch_Size, 1, 14)
    Classes: 3 (Healthy, Moderate Stress, No-Vegetation)
    """
    def __init__(self, in_features=14, num_classes=3):
        super(VegHealthCNN, self).__init__()
        
        self.feature_extractor = nn.Sequential(
            # Block 1
            nn.Conv1d(in_channels=1, out_channels=32, kernel_size=3, padding=1),
            nn.BatchNorm1d(32),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.2),
            
            # Block 2
            nn.Conv1d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            
            # Block 3
            nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.4),
        )
        
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        self.classifier = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            nn.Linear(64, num_classes)
        )
        
    def forward(self, x):
        # x: (batch_size, in_features) -> unsqueeze to (batch_size, 1, in_features)
        if x.dim() == 2:
            x = x.unsqueeze(1)
        feat = self.feature_extractor(x)
        pooled = self.global_pool(feat).squeeze(-1)
        logits = self.classifier(pooled)
        return logits

if __name__ == "__main__":
    model = VegHealthCNN(in_features=14, num_classes=3)
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"VegHealthCNN instantiated successfully! Total trainable parameters: {total_params:,}")

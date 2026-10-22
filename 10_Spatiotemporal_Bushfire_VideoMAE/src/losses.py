"""
Class-Balanced Focal Loss for Severe Geospatial Class Imbalance.
Specially designed for active wildfire/bushfire spread where positive
fire pixels constitute < 1.5% of the total landscape area.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class ClassBalancedFocalLoss(nn.Module):
    """
    Binary Focal Loss with dynamic alpha weighting for active fire pixel forecasting.
    FL(p_t) = -alpha * (1 - p_t)^gamma * log(p_t)
    """
    def __init__(self, alpha=0.75, gamma=2.0, reduction='mean'):
        super(ClassBalancedFocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, logits, targets):
        """
        logits:  (B, 1, H, W) raw unnormalized logits
        targets: (B, 1, H, W) ground truth binary masks {0, 1}
        """
        probs = torch.sigmoid(logits)
        bce_loss = F.binary_cross_entropy_with_logits(logits, targets, reduction='none')
        
        # p_t: probability of true class
        p_t = probs * targets + (1 - probs) * (1 - targets)
        
        # Alpha weighting for positive vs negative class
        alpha_t = self.alpha * targets + (1 - self.alpha) * (1 - targets)
        
        # Modulating factor
        focal_weight = alpha_t * ((1 - p_t) ** self.gamma)
        
        loss = focal_weight * bce_loss
        
        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        else:
            return loss

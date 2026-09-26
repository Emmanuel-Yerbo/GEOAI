import torch
import torch.nn.functional as F

class GradCAM:
    """
    Gradient-weighted Class Activation Mapping (Grad-CAM) for Convolutional Flood Segmentation Networks.
    Hooks into final convolutional layer to visualize spatial decision boundaries.
    """
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        target_layer.register_forward_hook(self._save_activation)
        target_layer.register_full_backward_hook(self._save_gradient)
        
    def _save_activation(self, module, input, output):
        self.activations = output
        
    def _save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]
        
    def generate_heatmap(self, input_tensor, class_idx=1):
        self.model.zero_grad()
        output = self.model(input_tensor)
        target = output[:, class_idx, :, :].sum()
        target.backward(retain_graph=True)
        
        pooled_gradients = torch.mean(self.gradients, dim=[0, 2, 3])
        for i in range(self.activations.size(1)):
            self.activations[:, i, :, :] *= pooled_gradients[i]
            
        heatmap = torch.mean(self.activations, dim=1).squeeze()
        heatmap = F.relu(heatmap)
        heatmap /= torch.max(heatmap) + 1e-8
        return heatmap.cpu().detach().numpy()

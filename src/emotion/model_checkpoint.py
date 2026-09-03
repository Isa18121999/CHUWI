import torch


def save_best_model(model, path, metric):
    torch.save({
        'model_state_dict': model.state_dict(),
        'metric': metric
    }, path)


def load_model(model, path):
    checkpoint = torch.load(path)
    model.load_state_dict(checkpoint['model_state_dict'])
    return checkpoint.get('metric')

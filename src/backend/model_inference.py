import torch
from src.buildteam.algorithm import TeamTransformer
from src.buildteam.dataloader import create_test_loader



def load_model(weights_path, params):
    model = TeamTransformer(**params)
    state_dict = torch.load(weights_path, map_location=torch.device('cpu'))
    model.load_state_dict(state_dict)
    model.eval()
    return model

def predict_with_model(model, data, batch_size=512):
    test_loader = create_test_loader(data, batch_size)
    predictions_list = []
    transformer_out_list = []

    for batch_inputs, _ in test_loader:
        with torch.no_grad():
            inputs = batch_inputs[:, :, :-2]
            inputs_num = batch_inputs[:, :, -2:].int()
            predictions, transformer_out = model(inputs)
            predictions_list.append(predictions)
            transformer_out_list.append(transformer_out)

    return predictions_list, transformer_out_list

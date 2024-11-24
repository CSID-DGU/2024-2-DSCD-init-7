import torch
from algorithm import TeamTransformer
from dataloader import create_test_loader

def load_model_weights(model_path, embedding_dim, seq_len, output_dim, n_heads, n_layers, hidden_dim, dropout_rate):
    model = TeamTransformer(
        embedding_dim=embedding_dim,
        n_heads=n_heads,
        hidden_dim=hidden_dim,
        n_layers=n_layers,
        output_dim=output_dim,
        dropout_rate=dropout_rate,
    )
    state_dict = torch.load(model_path, map_location=torch.device('cpu'))
    model.load_state_dict(state_dict)
    model.eval()
    return model

def make_predictions(model, final_data_f, batch_size):
    test_loader = create_test_loader(final_data_f, batch_size)
    predictions_list = []
    transformer_out_list = []

    for batch_inputs_total, _ in test_loader:
        with torch.no_grad():
            val_inputs_total, val_targets = next(iter(test_loader))
            val_inputs = batch_inputs_total[:, :, :-2]
            val_inputs_num = batch_inputs_total[:, :, -2:].int()
            predictions, transformer_out = model(val_inputs)
            predictions_list.append(predictions)
            transformer_out_list.append(transformer_out.detach().cpu().numpy())

    return predictions_list, transformer_out_list

import sys
sys.path.append('../')
from models import DenseModel
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
import pandas as pd
from torch import nn
import torch
import numpy as np
from tqdm import tqdm, trange

boston = load_boston()
df = pd.DataFrame(boston.data, columns=boston.feature_names)
df['PRICE'] = boston.target
X, y = df.drop('PRICE', 1), df['PRICE']

train_X, test_X, train_y, test_y = train_test_split(X, y, train_size=0.8)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
train_X, test_X, train_y, test_y = \
    [torch.from_numpy(np.array(x)).float().to(device)
     for x in [train_X, test_X, train_y, test_y]]

model = DenseModel(input_shape=train_X.shape[1], output_shape=1,
                   activation=nn.functional.relu).to(device)
opt = torch.optim.Adam(model.parameters(), lr=1e-2)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(opt, 'min')
criterion = nn.MSELoss()

n_epoches = 100000
debug_frequency = 100

pbar = trange(n_epoches, leave=True, position=0)
for epoch in pbar:
    opt.zero_grad()
    preds = model(train_X).squeeze()
    loss = criterion(preds, train_y)
    loss.backward()
    # scheduler.step(loss)
    opt.step()
    loss_train = float(criterion(preds, train_y).detach().cpu().numpy())
    preds = model(test_X).squeeze()
    loss_test = float(criterion(preds, test_y).detach().cpu().numpy())
    pbar.set_description('MSE (train): %.3f\tMSE (test): %.3f' %
                         (loss_train, loss_test))
    pbar.update()

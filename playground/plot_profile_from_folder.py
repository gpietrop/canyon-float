import os
import pandas as pd
import torch
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt

# from conv1med import Conv1dMed
from architecture.conv1med2 import Conv1dMed
from architecture.mlp import MLPDay, MLPYear, MLPLon, MLPLat
from dataset import FloatDataset

# Where to search the model
dir = "result-dp/"
date = "2022-12-20/"
ep = 525

# Upload the input ds
path_float = "/home/gpietropolli/Desktop/canyon-float/ds/float_ds_sf.csv"
dataset = FloatDataset(path_float)
ds = DataLoader(dataset, shuffle=True)

dir_model = "/home/gpietropolli/Desktop/canyon-float/" + dir + date + "model"
# dir_profile = dir + "/profile"

dir_info = "/home/gpietropolli/Desktop/canyon-float/" + dir + date + "info.csv"
info_df = pd.read_csv(dir_info)
dp_rate = info_df['dp_rate'].item()

# Path of the saved models
path_model_day = dir_model + "/model_day_" + str(ep) + ".pt"
path_model_year = dir_model + "/model_year_" + str(ep) + ".pt"
path_model_lon = dir_model + "/model_lon_" + str(ep) + ".pt"
path_model_lat = dir_model + "/model_lat_" + str(ep) + ".pt"
path_model_conv = dir_model + "/model_conv_" + str(ep) + ".pt"

# Upload and evaluate all the models necessary
model_day = MLPDay()
model_day.load_state_dict(torch.load(path_model_day))
model_day.eval()

model_year = MLPYear()
model_year.load_state_dict(torch.load(path_model_year))
model_year.eval()

model_lat = MLPLat()
model_lat.load_state_dict(torch.load(path_model_lat))
model_lat.eval()

model_lon = MLPLon()
model_lon.load_state_dict(torch.load(path_model_lon))
model_lon.eval()

model = Conv1dMed(dp_rate=dp_rate)
model.load_state_dict(torch.load(path_model_conv))
model.eval()

for year, day_rad, lat, lon, temp, psal, doxy, nitrate in ds:
    output_day = model_day(day_rad.unsqueeze(1))
    output_year = model_year(year.unsqueeze(1))
    output_lat = model_lat(lat.unsqueeze(1))
    output_lon = model_lon(lon.unsqueeze(1))

    output_day = torch.transpose(output_day.unsqueeze(0), 0, 1)
    output_year = torch.transpose(output_year.unsqueeze(0), 0, 1)
    output_lat = torch.transpose(output_lat.unsqueeze(0), 0, 1)
    output_lon = torch.transpose(output_lon.unsqueeze(0), 0, 1)
    temp = torch.transpose(temp.unsqueeze(0), 0, 1)
    psal = torch.transpose(psal.unsqueeze(0), 0, 1)
    doxy = torch.transpose(doxy.unsqueeze(0), 0, 1)
    nitrate = torch.transpose(nitrate.unsqueeze(0), 0, 1)

    x = torch.cat((output_day, output_year, output_lat, output_lon, temp, psal, doxy), 1)
    output_test = model(x.float())

    plt.plot(output_test[0, 0, :].detach().numpy(), label="generated nitrate")
    plt.plot(nitrate[0, 0, :].detach().numpy(), label="measured nitrate")
    plt.legend()
    # plt.savefig(dir_profile + f"/profile_{year}_{day_rad}_{round(lat, 2)}_{round(lon, 2)}.png")
    plt.show()
    plt.close()
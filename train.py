import os

import numpy as np
from IPython import display

import torch
from torch.optim import Adadelta
from torch.nn.functional import mse_loss

# from conv1med import Conv1dMed
from architecture.conv1med2 import Conv1dMed
from architecture.mlp import MLPDay, MLPYear, MLPLat, MLPLon


def train_model(train_loader, val_loader, epoch, lr, snaperiod, device, save_dir, verbose=False):

    model_mlp_day = MLPDay()
    model_mlp_year = MLPYear()
    model_mlp_lat = MLPLat()
    model_mlp_lon = MLPLon()
    model_conv = Conv1dMed()

    model_mlp_day.to(device)
    model_mlp_year.to(device)
    model_mlp_lat.to(device)
    model_mlp_lon.to(device)
    model_conv.to(device)

    params = list(model_mlp_day.parameters()) + list(model_mlp_year.parameters()) + list(
        model_mlp_lat.parameters()) + list(
        model_mlp_lon.parameters()) + list(model_conv.parameters())
    optimizer = Adadelta(params=params, lr=lr)

    f, f_test = open(save_dir + "/train_loss.txt", "w+"), open(save_dir + "/test_loss.txt", "w+")

    for ep in range(epoch):
        loss_train = []
        loss_test = []
        for training_year, training_day, training_lat, training_lon, training_temp, training_psal, training_doxy, training_nitrate in train_loader:

            # move data to device
            training_year = training_year.to(device)
            training_day = training_day.to(device)
            training_lat = training_lat.to(device)
            training_lon = training_lon.to(device)
            training_temp = training_temp.to(device)
            training_psal = training_psal.to(device)
            training_doxy = training_doxy.to(device)
            training_nitrate = training_nitrate.to(device)

            training_day = training_day.unsqueeze(1)
            output_day = model_mlp_day(training_day)

            training_year = training_year.unsqueeze(1)
            output_year = model_mlp_year(training_year.float())

            training_lat = training_lat.unsqueeze(1)
            output_lat = model_mlp_lat(training_lat.float())

            training_lon = training_lon.unsqueeze(1)
            output_lon = model_mlp_lon(training_lon.float())

            output_day = torch.transpose(output_day.unsqueeze(0), 0, 1)
            output_year = torch.transpose(output_year.unsqueeze(0), 0, 1)
            output_lat = torch.transpose(output_lat.unsqueeze(0), 0, 1)
            output_lon = torch.transpose(output_lon.unsqueeze(0), 0, 1)
            training_temp = torch.transpose(training_temp.unsqueeze(0), 0, 1)
            training_psal = torch.transpose(training_psal.unsqueeze(0), 0, 1)
            training_doxy = torch.transpose(training_doxy.unsqueeze(0), 0, 1)
            training_nitrate = torch.transpose(training_nitrate.unsqueeze(0), 0, 1)

            training_x = torch.cat(
                (output_day, output_year, output_lat, output_lon, training_temp, training_psal, training_doxy), 1)

            output = model_conv(training_x.float())

            loss_conv = mse_loss(training_nitrate, output)  # MSE
            loss_train.append(loss_conv.item())

            # print(model_conv.conv3.weight.mean())
            # print(model_mlp_lat.network[0].weight.mean())

            if verbose:
                print(f"[EPOCH]: {ep + 1}, [LOSS]: {loss_conv.item():.12f}")
                display.clear_output(wait=True)

            optimizer.zero_grad()
            loss_conv.backward()
            optimizer.step()

            # print(model_conv.conv1.weight[0])
        avg_train_loss = np.average(loss_train)
        print(f"[==== EPOCH]: {ep + 1}, [AVERAGE LOSS]: {avg_train_loss:.5f}")
        f.write(f"[EPOCH]: {ep + 1}, [LOSS]: {avg_train_loss:.5f} \n")

        # Saving model and testing
        if ep % snaperiod == 0:

            # Saving models at the considered ep
            torch.save(model_mlp_day.state_dict(), save_dir + "/model_day_" + str(ep) + ".pt")
            torch.save(model_mlp_year.state_dict(), save_dir + "/model_year_" + str(ep) + ".pt")
            torch.save(model_mlp_lat.state_dict(), save_dir + "/model_lat_" + str(ep) + ".pt")
            torch.save(model_mlp_lon.state_dict(), save_dir + "/model_lon_" + str(ep) + ".pt")
            torch.save(model_conv.state_dict(), save_dir + "/model_conv_" + str(ep) + ".pt")

            # Testing model
            model_mlp_day.eval()
            model_mlp_year.eval()
            model_mlp_lat.eval()
            model_mlp_lon.eval()
            model_conv.eval()

            with torch.no_grad():
                for testing_year, testing_day, testing_lat, testing_lon, testing_temp, testing_psal, testing_doxy, testing_nitrate in val_loader:

                    testing_year = testing_year.to(device)
                    testing_day = testing_day.to(device)
                    testing_lat = testing_lat.to(device)
                    testing_lon = testing_lon.to(device)
                    testing_temp = testing_temp.to(device)
                    testing_psal = testing_psal.to(device)
                    testing_doxy = testing_doxy.to(device)
                    testing_nitrate = testing_nitrate.to(device)

                    testing_day = testing_day.unsqueeze(1)
                    output_day_test = model_mlp_day(testing_day)

                    testing_year = testing_year.unsqueeze(1)
                    output_year_test = model_mlp_year(testing_year)

                    testing_lat = testing_lat.unsqueeze(1)
                    output_lat_test = model_mlp_lat(testing_lat)

                    testing_lon = testing_lon.unsqueeze(1)
                    output_lon_test = model_mlp_lon(testing_lon)

                    output_day_test = torch.transpose(output_day_test.unsqueeze(0), 0, 1)
                    output_year_test = torch.transpose(output_year_test.unsqueeze(0), 0, 1)
                    output_lat_test = torch.transpose(output_lat_test.unsqueeze(0), 0, 1)
                    output_lon_test = torch.transpose(output_lon_test.unsqueeze(0), 0, 1)
                    testing_temp = torch.transpose(testing_temp.unsqueeze(0), 0, 1)
                    testing_psal = torch.transpose(testing_psal.unsqueeze(0), 0, 1)
                    testing_doxy = torch.transpose(testing_doxy.unsqueeze(0), 0, 1)
                    testing_nitrate = torch.transpose(testing_nitrate.unsqueeze(0), 0, 1)

                    testing_x = torch.cat((output_day_test, output_year_test, output_lat_test, output_lon_test,
                                           testing_temp, testing_psal, testing_doxy), 1)

                    output_test = model_conv(testing_x.float())

                    loss_conv = mse_loss(testing_nitrate, output_test)
                    loss_test.append(loss_conv)

                    if verbose:
                        print(f"-----[EPOCH]: {ep + 1}, [TEST LOSS]: {loss_conv.item():.12f}")
                        display.clear_output(wait=True)

            avg_test_loss = np.average(loss_test)
            print(f"[==== EPOCH]: {ep + 1}, [AVERAGE TEST LOSS]: {avg_test_loss:.5f}")
            f_test.write(f"[EPOCH]: {ep + 1}, [TEST LOSS]: {avg_test_loss:.5f} \n")

    f.close()
    f_test.close()

# torch.save(model.state_dict(), "model/model2015/model_step1_ep_" + str(epoch_c + epoch_pretrain) + ".pt")

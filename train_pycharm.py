import time
from options.train_options import TrainOptions
from data.data_loader import CreateDataLoader
from models.models import create_model
from util.visualizer import Visualizer

# settings by sangkny after combining the script.py and train.py
import os
import argparse

def get_config(config):
    import yaml
    with open(config, 'r') as stream:
        return yaml.load(stream)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=str, default="8097")
    parser.add_argument("--train", action='store_true')
    parser.add_argument("--predict", action='store_true')

    opt = parser.parse_args()
    opt.train = True
    opt.dataroot ='./datasets/lol/final_dataset'
    #
    # if opt.train:
    #     os.system("python train.py \
    # 		--dataroot ../final_dataset \
    # 		--no_dropout \
    # 		--name enlightening \
    # 		--model single \
    # 		--dataset_mode unaligned \
    # 		--which_model_netG sid_unet_resize \
    #         --which_model_netD no_norm_4 \
    #         --patchD \
    #         --patch_vgg \
    #         --patchD_3 5 \
    #         --n_layers_D 5 \
    #         --n_layers_patchD 4 \
    # 		--fineSize 320 \
    #         --patchSize 32 \
    # 		--skip 1 \
    # 		--batchSize 32 \
    #         --self_attention \
    # 		--use_norm 1 \
    # 		--use_wgan 0 \
    #         --use_ragan \
    #         --hybrid_loss \
    #         --times_residual \
    # 		--instance_norm 0 \
    # 		--vgg 1 \
    #         --vgg_choose relu5_1 \
    # 		--gpu_ids 0,1,2 \
    # 		--display_port=" + opt.port)
    opt = TrainOptions().parse()
    config = get_config(opt.config)
    data_loader = CreateDataLoader(opt)
    dataset = data_loader.load_data()
    dataset_size = len(data_loader)
    print('#training images = %d' % dataset_size)

    model = create_model(opt)
    visualizer = Visualizer(opt)

    total_steps = 0

    for epoch in range(1, opt.niter + opt.niter_decay + 1):
        epoch_start_time = time.time()
        for i, data in enumerate(dataset):
            iter_start_time = time.time()
            total_steps += opt.batchSize
            epoch_iter = total_steps - dataset_size * (epoch - 1)
            model.set_input(data)
            model.optimize_parameters(epoch)

            if total_steps % opt.display_freq == 0:
                visualizer.display_current_results(model.get_current_visuals(), epoch)

            if total_steps % opt.print_freq == 0:
                errors = model.get_current_errors(epoch)
                t = (time.time() - iter_start_time) / opt.batchSize
                visualizer.print_current_errors(epoch, epoch_iter, errors, t)
                if opt.display_id > 0:
                    visualizer.plot_current_errors(epoch, float(epoch_iter)/dataset_size, opt, errors)

            if total_steps % opt.save_latest_freq == 0:
                print('saving the latest model (epoch %d, total_steps %d)' %
                      (epoch, total_steps))
                model.save('latest')

        if epoch % opt.save_epoch_freq == 0:
            print('saving the model at the end of epoch %d, iters %d' %
                  (epoch, total_steps))
            model.save('latest')
            model.save(epoch)

        print('End of epoch %d / %d \t Time Taken: %d sec' %
              (epoch, opt.niter + opt.niter_decay, time.time() - epoch_start_time))

        if opt.new_lr:
            if epoch == opt.niter:
                model.update_learning_rate()
            elif epoch == (opt.niter + 20):
                model.update_learning_rate()
            elif epoch == (opt.niter + 70):
                model.update_learning_rate()
            elif epoch == (opt.niter + 90):
                model.update_learning_rate()
                model.update_learning_rate()
                model.update_learning_rate()
                model.update_learning_rate()
        else:
            if epoch > opt.niter:
                model.update_learning_rate()

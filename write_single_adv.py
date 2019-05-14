#!/usr/bin/env python

import os
import sys
import argparse

sys.path.append(os.getcwd())
import tensorflow as tf

from lsgn_data import LSGNData
from lsgn_evaluator_writer import LSGNEvaluator
from srl_model import SRLModel
import util


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_path", type=str,
                        help="path of the output file", default=None)
    parser.add_argument("-e", "--eps", type=float,
                        help="size of the perturbation", default=0)
    parser.add_argument("-m", "--method", type=str,
                        choices=["fgsm", "rand"],
                        help="perturbation method", default="fgsm")
    parser.add_argument("name", type=str,
                        help="name of the experiment", default=None)
    args = parser.parse_args()

    if args.name is not None:
        name = args.name
        print("Running experiment: {} (from environment variable).".format(name))
    else:
        name = os.environ["EXP"]
        print("Running experiment: {} (from command-line argument).".format(name))

    config = util.get_config("experiments.conf")[name]
    config["log_dir"] = util.mkdirs(os.path.join(config["log_root"], name))

    config["batch_size"] = -1
    config["max_tokens_per_batch"] = -1

    # Use dev lm, if provided.
    if config["lm_path"] and "lm_path_dev" in config and config["lm_path_dev"]:
        config["lm_path"] = config["lm_path_dev"]

    config["adv"] = True
    config["adv_eps"] = args.eps
    config["adv_method"] = args.method  # or "rand" for random perturbation

    config["output_path"] = args.output_path

    print("---" * 60)
    util.print_config(config)
    print("---" * 60)
    #    exit(0)
    data = LSGNData(config)
    model = SRLModel(data, config)
    evaluator = LSGNEvaluator(config)

    variables_to_restore = []
    for var in tf.global_variables():
        print(var.name)
        if "module/" not in var.name:
            variables_to_restore.append(var)

    saver = tf.train.Saver(variables_to_restore)
    log_dir = config["log_dir"]

    with tf.Session() as session:
        checkpoint_path = os.path.join(log_dir, "model.max.ckpt")
        print("Evaluating {}".format(checkpoint_path))
        tf.global_variables_initializer().run()
        saver.restore(session, checkpoint_path)
        evaluator.evaluate(session, data, model.predictions, model.loss)


if __name__ == "__main__":
    main()

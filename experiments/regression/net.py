import sys

import torch
from experiments.regression.data_processor import RegressionPreprocessor
from fedrec.utilities import registry
from torch import nn, sigmoid

### define LogisticRegression in PyTorch ###


@registry.load("model", "regression")
class Regression_Net(nn.Module):
    Preproc = RegressionPreprocessor

    def __init__(
        self,
        preprocessor: RegressionPreprocessor,
        input_dim=784,
        output_dim=10,
        loss_weights=None,
        loss_threshold=0.0,
        ndevices=-1,
        loss_function="mse"
    ):
        super().__init__()
        self.preproc = preprocessor
        self.ndevices = ndevices
        self.output_dim = output_dim
        self.input_dim = input_dim
        self.parallel_model_batch_size = -1
        self.parallel_model_is_not_prepared = True
        self.loss_threshold = loss_threshold
        self.loss_function = loss_function

        self.linear = torch.nn.Linear(self.input_dim, self.output_dim, True)

        # specify the loss function
        if self.loss_function == "mse":
            self.loss_fn = torch.nn.MSELoss(reduction="mean")
        elif self.loss_function == "ce":
            self.loss_fn = torch.nn.CrossEntropyLoss(
                reduction="mean")
        else:
            sys.exit(
                "ERROR: --loss_function="
                + self.loss_function
                + " is not supported"
            )

    def forward(self, x):
        out = self.linear(x.reshape(-1, self.input_dim))

        if 0.0 < self.loss_threshold < 1.0:
            out = torch.clamp(out, min=self.loss_threshold,
                              max=(1.0 - self.loss_threshold))
        return out

    def get_scores(self, logits):
        return sigmoid(logits)

    def loss(self, logits, true_label):
        if self.loss_function == "mse":
            return self.loss_fn(self.get_scores(logits), true_label)
        elif self.loss_function == "ce":
            return self.loss_fn(logits, true_label)

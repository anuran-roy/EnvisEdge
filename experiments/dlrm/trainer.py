from typing import Dict

import attr
from fedrec.user_modules.envis_trainer import EnvisTrainer
from fedrec.utilities import registry
from fedrec.utilities.logger import BaseLogger


@attr.s
class DLRMTrainConfig:
    eval_every_n = attr.ib(default=10000)
    report_every_n = attr.ib(default=10)
    save_every_n = attr.ib(default=2000)
    keep_every_n = attr.ib(default=10000)

    batch_size = attr.ib(default=128)
    eval_batch_size = attr.ib(default=256)
    num_epochs = attr.ib(default=-1)

    num_batches = attr.ib(default=-1)

    @num_batches.validator
    def check_only_one_declaration(self, _, value):
        if self.num_epochs > 0 & value > 0:
            raise ValueError(
                "only one out of num_epochs and num_batches must be declared!")

    num_eval_batches = attr.ib(default=-1)
    eval_on_train = attr.ib(default=False)
    eval_on_val = attr.ib(default=True)

    num_workers = attr.ib(default=0)
    pin_memory = attr.ib(default=True)


@registry.load('trainer', 'dlrm')
class DLRMTrainer(EnvisTrainer):

    def __init__(
            self,
            config_dict: Dict,
            logger: BaseLogger,
            client_id=None) -> None:

        super().__init__(config_dict, logger, client_id)
        self.train_config = DLRMTrainConfig(
            **config_dict["trainer"]["config"]
        )

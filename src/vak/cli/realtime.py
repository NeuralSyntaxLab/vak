import logging
from pathlib import Path

from .. import (
    config,
    core
)
from ..logging import config_logging_for_cli, log_version


logger = logging.getLogger(__name__)


def realtime(toml_path):
    """make predictions on dataset with trained model specified in config.toml file.
    Function called by command-line interface.

    Parameters
    ----------
    toml_path : str, Path
        path to a configuration file in TOML format.
    """
    toml_path = Path(toml_path)
    cfg = config.parse.from_toml_path(toml_path)

    if cfg.realtime is None:
        raise ValueError(
            f"realtime called with a config.toml file that does not have a REALTIME section: {toml_path}"
        )

    # ---- set up logging ----------------------------------------------------------------------------------------------
    config_logging_for_cli(
        log_dst=cfg.realtime.output_dir,
        log_stem="realtime",
        level="INFO",
        force=True
    )
    log_version(logger)
    logger.info("Logging results to {}".format(cfg.prep.output_dir))

    model_config_map = config.models.map_from_path(toml_path, cfg.realtime.models)

    core.realtime(
        triggers=cfg.realtime.triggers,
        checkpoint_path=cfg.realtime.checkpoint_path,
        labelmap_path=cfg.realtime.labelmap_path,
        model_config_map=model_config_map,
        window_size=cfg.dataloader.window_size,
        num_workers=cfg.realtime.num_workers,
        spect_key=cfg.spect_params.spect_key,
        timebins_key=cfg.spect_params.timebins_key,
        spect_scaler_path=cfg.realtime.spect_scaler_path,
        device=cfg.realtime.device,
        annot_csv_filename=cfg.realtime.annot_csv_filename,
        output_dir=cfg.realtime.output_dir,
        min_segment_dur=cfg.realtime.min_segment_dur,
        majority_vote=cfg.realtime.majority_vote,
        save_net_outputs=cfg.realtime.save_net_outputs,
    )

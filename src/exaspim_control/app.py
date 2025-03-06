"""
CLI Application for exaspim control and testing.
"""

import click


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--simulated", "-s", is_flag=True, help="Launch the simulated ExASPIM application.")
def cli(ctx: click.Context, simulated: bool) -> None:
    """
    CLI for controlling and testing ExASPIM.

    :param ctx: Click context
    :type ctx: click.Context
    :param simulated: Flag to launch the simulated ExASPIM application
    :type simulated: bool
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(launch, simulated=simulated)


@cli.command()
@click.argument("config_path", type=click.Path(exists=True), required=False)
@click.option("--simulated", "-s", is_flag=True, help="Launch the simulated ExASPIM application.")
def launch(config_path: str, simulated: bool) -> None:
    """
    Launch the ExASPIM application.

    :param config_path: Path to the configuration file
    :type config_path: str
    :param simulated: Flag to launch the simulated ExASPIM application
    :type simulated: bool
    """

    def launch_simulated() -> None:
        """
        Launch the simulated ExASPIM application.
        """
        from exaspim_control.simulated.main import launch_simulated_exaspim
        launch_simulated_exaspim()

    def launch_real_device() -> None:
        from exaspim_control.experimental.main import launch_exaspim
        launch_exaspim()

    if simulated:
        click.echo(f"Running using simulated devices")
        launch_simulated()
    else:
        click.echo(f"Running using physical devices")
        launch_real_device()

@cli.command()
@click.option("--stage-motion", "-s", is_flag=True, help="Test stage movement",default=False)
@click.option("--fix-rotary", "-r", is_flag=True, help="Setup rotary encoder",default=False)
def debug(stage_motion : bool, fix_rotary : bool):
    from exaspim_control.debug_tools.stage import StageInstrument
    if stage_motion :
        StageInstrument().stage_motion_run()
    elif fix_rotary:
        StageInstrument().set_rotary_encoder()
    else :
        raise ValueError("You must supply a debug test to run")

if __name__ == "__main__":
    cli()

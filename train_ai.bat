@echo off
set run_id=%1
set /A num_envs = %2

IF "%run_id%"=="" GOTO MissingRunIDError

call .venv\Scripts\activate

GOTO CheckNewRunID


:CheckNewRunID
	set /p "resume_training=Are you using a pre-existing run-id? (Y/N) or X to cancel. "
	IF /I "%resume_training%" == "Y" GOTO StartTraining
	IF /I "%resume_training%" == "N" GOTO StartTraining
	IF /I "%resume_training%" == "X" exit /B
	IF not /I "%resume_training%" == "Y" GOTO InvalidRunIDBoolean (
		IF not /I "%resume_training%" == "N" GOTO InvalidRunIDBoolean (
			IF not /I "'%resume_training%" == "X" GOTO InvalidRunIDBoolean(
				GOTO InvalidRunIDBoolean
		)
	)
)

:MissingRunIDError
	echo Run ID is missing.
:InvalidRunIDBoolean
	echo Invalid option. Please enter Y or N for yes or no respectively, or X to cancel.
	GOTO CheckNewRunID

:StartTraining
	IF /I "%resume_training%" == "Y" call mlagents-learn training_config.yaml --run-id=%run_id% --resume
	IF /I "%resume_training%" == "N" call mlagents-learn training_config.yaml --run-id=%run_id%
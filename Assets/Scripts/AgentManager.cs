using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;

public class AgentManager : Agent
{

    public GameObject instanceManagerGO;
    private InstanceManager instanceManager;
    GameMode gameMode;
    public SlotStatuses agent_colour;
    public bool plays_second;

    private void Awake()
    {
        instanceManager = instanceManagerGO.GetComponent<InstanceManager>();
        gameMode = instanceManager.gameMode;
        instanceManager.turn_played = plays_second;
    }

    public void DoEnable()
    {
        if (gameObject.activeSelf)
        {
            MaxStep = 128;
            if(instanceManager.gameMode == GameMode.PvAI) { MaxStep = 0; }
            Academy.Instance.OnEnvironmentReset += instanceManager.StartGame;
            if (!plays_second)
            {
                RequestDecision();
            }
        }
    }


    public override void OnActionReceived(ActionBuffers actions)
    {
        if (gameObject.activeSelf)
        {
            if (instanceManager.turn_played && (gameMode == GameMode.AIvAI || gameMode == GameMode.RvAI || gameMode == GameMode.PvAI) && !instanceManager.gameFinished)
            {
                instanceManager.PlayTurn(actions.DiscreteActions[0]);
            }
            instanceManager.turn_played = true;
            if (gameMode == GameMode.PvAI)
            {
                instanceManager.turn_played = false;
            }
        }
    }
    private bool CanCollectObservations()
    {
        if ((gameMode == GameMode.AIvAI) ||
            ((gameMode == GameMode.RvAI || gameMode == GameMode.PvAI) &&
            agent_colour == instanceManager.ai_colour))
        {
            return true;
        }

        else { return false; }
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        if (gameObject.activeSelf)
        {
            sensor.AddObservation((int)agent_colour);
            if (CanCollectObservations())
            {
                switch (AgentConstants.observationType)
                {
                    case ObservationType.NormalisedArray:
                        sensor.AddObservation(instanceManager.LGetNormalisedMatrix());
                        break;
                    case ObservationType.Array:
                        sensor.AddObservation((IList<float>)instanceManager.LGetMatrix());
                        break;
                    case ObservationType.NormalisedHash:
                        sensor.AddObservation(instanceManager.NormaliseBoardHash(instanceManager.GetBoardHash()));
                        break;
                    case ObservationType.Hash:
                        sensor.AddObservation(instanceManager.GetBoardHash());
                        break;

                }
            }
            instanceManager.cumReward.text = "Cumulative reward: " + GetCumulativeReward().ToString();
        }
    }

    /*
    public override void Heuristic(in ActionBuffers actionsOut)
    {
        if (gameObject.activeSelf)
        {
            if(gameMode == GameMode.PvAI)
            {
                if (instanceManager.turn_played && !instanceManager.gameFinished)
                {
                    instanceManager.PlayTurn(actionsOut.DiscreteActions[0]);
                }
                instanceManager.turn_played = false;
            }
        }
    }
    */

    public override void OnEpisodeBegin()
    {
        instanceManager.StartGame();
    }

    private void Update()
    {
        if (!Academy.Instance.IsCommunicatorOn && !(instanceManager.gameMode == GameMode.PvAI))
        {
            Debug.LogWarning("Warning: Communicator not detected.");
        }
        /*if(Academy.Instance.StepCount > MaxStep)
        {
            AddReward(AgentConstants.maxStepReward);
            EndEpisode();
            //Debug.LogWarning("Warning: Maximum step count exceeded");
        }*/
    }

    public void UpdateReward()
    {
        if (gameObject.activeSelf)
        {
            AddReward(instanceManager.GetReward(instanceManager.latest_winner, agent_colour));
            EndEpisode();
        }
    }
}

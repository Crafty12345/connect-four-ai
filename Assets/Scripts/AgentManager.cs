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

    public override void CollectObservations(VectorSensor sensor)
    {

        if (gameObject.activeSelf)
        {
            if (gameMode == GameMode.AIvAI)
            {
                sensor.AddObservation(instanceManager.GetStatuses(instanceManager.slots));
            }
            else if ((gameMode == GameMode.RvAI || gameMode == GameMode.PvAI) && agent_colour == instanceManager.ai_colour)
            {
                sensor.AddObservation(instanceManager.GetStatuses(instanceManager.slots));
            }

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

    public void UpdateReward()
    {
        if (gameObject.activeSelf)
        {
            SetReward(instanceManager.GetReward(instanceManager.latest_winner, agent_colour));
            EndEpisode();
        }
    }
}

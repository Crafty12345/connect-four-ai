using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AgentConstants: MonoBehaviour
{
    public static AgentConstants Instance { get; private set; }
    public static float winReward;
    public static float tieReward;
    public static float loseReward;
    public static float surviveReward;
    public static float blockReward;
    public static ObservationType observationType;

    private void Awake()
    {
        if(Instance != null && Instance != this)
        {
            Destroy(this);
        }
        else
        {
            Instance = this;
        }
    }

    private void Start()
    {
        AgentConstantData scriptableObjectData = Resources.Load<AgentConstantData>("Scriptable_Objects/agentConstantData");
        winReward = scriptableObjectData.winReward;
        tieReward = scriptableObjectData.tieReward;
        loseReward = scriptableObjectData.loseReward;
        surviveReward = scriptableObjectData.surviveReward;
        blockReward = scriptableObjectData.blockReward;
        observationType = scriptableObjectData.observationType;
    }
}

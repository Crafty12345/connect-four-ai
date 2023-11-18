using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[CreateAssetMenu(fileName ="agentConstantData",menuName ="Scriptable Objects/AgentConstantData")]
public class AgentConstantData: ScriptableObject
{
    public float winReward;
    public float tieReward;
    public float loseReward;
    public float surviveReward;
    public float blockReward;
    public ObservationType observationType;
}

public enum ObservationType
{
    Array,
    NormalisedArray,
    Hash,
    NormalisedHash
}
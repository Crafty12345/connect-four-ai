using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SlotData : MonoBehaviour
{

    public SlotStatuses slotStatus;
    
    public Color slot_colour;

    [Tooltip("(Columns, Rows)")]
    public List<int> pos = new List<int>(new int[2]);

    public GameObject gameManagerObj;

    //NOTE: slotID is zero-based
    public int slotID;

    private Dictionary<string, Color> colourData;
    private bool isInitialised;

    // Start is called before the first frame update
    void Start()
    {
        isInitialised = false;
        colourData = gameManagerObj.GetComponent<InstanceManager>().colourData;
        if(colourData == null)
        {
            gameManagerObj.GetComponent<InstanceManager>().InitialiseColourData();
            colourData = gameManagerObj.GetComponent<InstanceManager>().colourData;
        }
        
        slot_colour = colourData[slotStatus.ToString()];
        gameObject.GetComponent<SpriteRenderer>().color = slot_colour;
        isInitialised = true;
    }

    public void UpdateSlotStatus(SlotStatuses new_status)
    {
        
        if(colourData==null)
        {
            colourData = gameManagerObj.GetComponent<InstanceManager>().colourData;
        }

        slotStatus = new_status;
        SpriteRenderer dbgRenderer = gameObject.GetComponent<SpriteRenderer>();
        slot_colour = colourData[slotStatus.ToString()];
        gameObject.GetComponent<SpriteRenderer>().color = slot_colour;
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}

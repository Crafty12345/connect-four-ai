using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PointerData : MonoBehaviour
{

    public byte selected_col;
    public int n_cols;
    public GameObject gameManager;
    public SlotStatuses status;
    public List<float> col_positions = new List<float>();

    public void UpdateColour()
    {
        gameObject.GetComponent<SpriteRenderer>().color = gameManager.GetComponent<InstanceManager>().colourData[status.ToString()];
    }
    public void UpdatePosition(sbyte new_pos)
    {
        if (new_pos != -1 && new_pos < n_cols)
        {
            selected_col = (byte)new_pos;
            transform.position = new Vector2(col_positions[new_pos], transform.position.y);
        }
        
    }

    public void SetStatus(SlotStatuses status)
    {
        this.status = status;
        UpdateColour();
    }
}
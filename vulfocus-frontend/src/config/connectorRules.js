let connectorRules = [
	{
	  type:'Container',
	  canBeContainedType:[],
    canLinkToType: ['Network']
  },
	{
	  type:'Network',
	  canBeContainedType:[],
	  canLinkToType:['Container']
	}
]
export default connectorRules

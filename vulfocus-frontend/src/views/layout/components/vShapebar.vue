<!--
 * @Author: caojing
 * @Date: 2018-11-23 10:28:53
 * @LastEditors: r4v3zn
 * @LastEditTime: 2018-11-27 10:12:26
 -->
<template>
    <div class="shapebarWrap">
        <div class="shapebarHead">
            环境类型
        </div>
        <div class="shapeNodeLstWrap">
            <ul class="shapeNodeLst">
                <li v-for="(ele,key) in shapeNodeLstData" :key="key" class="shapeNode" @mousedown.stop.prevent = "dragShapeNode(shapeNodeLstData,key,$event)" :title="ele.type">
                <div class="shapeIcon">
                    <img class="shapeIconImg" :src="ele.icon"  alt=""/>
                </div>
                <div class="shapeName">{{ele.type}}</div>
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
import shapeNodeLstData from '@/config/toolbarNodeData'
export default {
  name:'vShapebar',
  data(){
   return {
       shapeNodeLstData:[]
   }
  },
  components: {

  },
  methods:{
    dragShapeNode(shapeNodeLstData,key,$event){
          this.$emit('click', shapeNodeLstData,key,$event);
    },
    //初始shapeLstData
    initToolbarNodes(){
      let initShapeLstData = shapeNodeLstData
      if(!initShapeLstData instanceof Array){
          initShapeLstData = []
      }
      this.shapeNodeLstData = initShapeLstData
    }
  },
  mounted(){
      this.initToolbarNodes()
  },
  created(){}
}
</script>
<style lang="less" scoped>
@border-color:#aaaaaa;
/*svgMain左侧工具栏*/
.shapebarWrap{
  height:100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  width: 250px;
  border: 1px solid @border-color;
  border-right:0;
  background:#f3f3f3;
  .shapebarHead{
    height: 40px;
    line-height: 40px;
    text-align: center;
    font-size: 14px;
    -webkit-user-select:none;
    user-select:none;
    font-weight: 700;
    color:#525252;
    text-overflow:ellipsis;
    overflow:hidden;
    white-space:nowrap;
  }
  .shapeNodeLstWrap{
    overflow-y: auto;
    box-sizing:border-box;
    padding: 10px 15px;
    flex: 1;
    .shapeNodeLst{
      width: 100%;
      display: flex;
      flex-wrap: wrap;
      box-sizing: border-box;
    }
  }
}
.shapeNode{
  list-style: none;
  margin-top: 10px;
  cursor: pointer;
  border:1px solid #c7d1dd;
  border-radius: 2px;
  -webkit-user-select:none;
  user-select:none;
  background-color: #fff;
  box-sizing: border-box;
  width: 70%;
  padding:8px 0;
  margin-right: 5px;
    &:nth-child(2n){margin-right: 0}
}
/*移动的node*/
.shapeIcon{text-align: center;-webkit-user-select:none;user-select:none;
  .shapeIconImg{width: 28px;height: 28px;-webkit-user-select:none;user-select:none;}
}
.shapeName{font-size:12px;text-align: center;padding:0 5px;text-overflow:ellipsis;overflow:hidden;white-space:nowrap;-webkit-user-select:none;user-select:none;color:#000}
</style>

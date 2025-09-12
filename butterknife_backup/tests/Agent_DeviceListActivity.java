package com.zhongxun.gps365.titleact;

import static com.zhongxun.gps365.util.DateUtil.transform;
import static com.zhongxun.gps365.util.IOUtils.ChangeIP;
import static com.zhongxun.gps365.util.IOUtils.log;

import android.annotation.SuppressLint;
import android.app.AlertDialog;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.widget.AdapterView;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.zhongxun.gps365.R;
import com.zhongxun.gps365.ZhongXunApplication;
import com.zhongxun.gps365.adapter.CommonAdapter;
import com.zhongxun.gps365.adapter.ViewHolder;
import com.zhongxun.gps365.bean.DeviceInfo;
import com.zhongxun.gps365.bean.DeviceListBean;
import com.zhongxun.gps365.startact.BaseActivity;
import com.zhongxun.gps365.util.Config;
import com.zhongxun.gps365.util.DeviceStatusStringUtils;
import com.zhongxun.gps365.util.MapUtil;
import com.zhongxun.gps365.util.RegisterReceiverHelper;
import com.zhongxun.gps365.util.UIUtils;
import com.zhongxun.gps365.widget.MProgressDilog;
import com.zhy.http.okhttp.OkHttpUtils;
import com.zhy.http.okhttp.callback.StringCallback;

import org.json.JSONArray;
import org.json.JSONObject;

import java.text.ParsePosition;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.TimeZone;
import java.util.Timer;
import java.util.TimerTask;

import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;
import okhttp3.Call;

public class Agent_DeviceListActivity extends BaseActivity implements AdapterView.OnItemClickListener {
    @BindView(R.id.listview) ListView listview;
    @BindView(R.id.tvAll) TextView tvAll;
    @BindView(R.id.tvAllDeivces) TextView tvAlltvAllDeivces;
    @BindView(R.id.finddevice) EditText finddevice;//密码
    @BindView(R.id.tbCancel) TextView tbCancel;
    @BindView(R.id.tvAgent) TextView tvAgent;
    @BindView(R.id.tbFind) TextView tbFind;
    TextView tvDevices;
    private List<DeviceListBean> allListBeans = new ArrayList<DeviceListBean>();//所有
    private List<DeviceListBean> findListBeans = new ArrayList<DeviceListBean>();//离线

    private DeviceAdapter allAdapter;
    private DeviceAdapter findAdapter;

    private Timer timer = new Timer();
    private String user;
    private String word;
    private Boolean flag = false;//是否弹出的标识符
    private ScreenStatusReceiver receiver;
    private int refreshTime;
    private SwipeRefreshLayout mRefreshLayout;// SwipeRefreshLayout下拉刷新控件
    private int neterr = 0 ;
    @Override
    public void onBackPressed() {
        finish();
        return;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        setContentView(R.layout.agent_device_lists);
        ButterKnife.bind(this);
        //log("Agent Device list onCreate");
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN);
        tvDevices = (TextView) findViewById(R.id.tvDevices);
        mRefreshLayout = (SwipeRefreshLayout) findViewById(R.id.mRefreshLayout);
        mRefreshLayout.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                mRefreshLayout.post(new Runnable() {
                    @Override
                    public void run() {
                        if ( !Config.agent ) {
                            if (!isConnected().equals("NULL")) {
                                mRefreshLayout.setRefreshing(false);
                                user = preferenceUtil.getString(Config.USERNAME);
                                word = preferenceUtil.getString(Config.PASSWORD);
                                getDeviceInfos(user, word, 1);
                            } else {
                                Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.net_no_link), Toast.LENGTH_SHORT).show();
                            }
                        }
                    }
                });
            }
        });

        mProgressDilog = new MProgressDilog(this);
        if (mProgressDilog != null) {
            mProgressDilog.dissmissProgressDilog();
        }

        if ( Config.agent ) {
            tvAgent.setVisibility(View.INVISIBLE);
            tvDevices.setText( Config.PW + " " + UIUtils.getString(R.string.device_list));
            if ( !Config.MasterAgent.equals("") ) {
                String AG = Config.MasterAgent;
                //log("AG:" + AG);
                if (!isConnected().equals("NULL")) {
                    getAgentDeviceInfos(AG);
                } else
                    Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.net_no_link), Toast.LENGTH_SHORT).show();
            } else {
                //log("AG1:NU"  );
            }
        } else {
            tvAgent.setVisibility(View.INVISIBLE);
            initAllData();
            initOtherData();
        }
        allAdapter = new DeviceAdapter(Agent_DeviceListActivity.this, allListBeans, R.layout.item_agentdevicelist);
        listview.setAdapter(allAdapter);//设置默认
        initEvent();
        IntentFilter filter = new IntentFilter();
        filter.addAction("android.intent.action.SCREEN_OFF");
        filter.addAction("android.intent.action.SCREEN_ON");
        RegisterReceiverHelper.registerReceiver(mContext,receiver, filter);

        finddevice = (EditText) findViewById(R.id.finddevice);
        finddevice.addTextChangedListener(textWatcher);
        /*finddevice.setOnKeyListener(new View.OnKeyListener() {
            public boolean onKey(View v, int keyCode, KeyEvent event) {
               if (  keyCode == KeyEvent.KEYCODE_ENTER ) {
                   if ( !Config.MasterAgent.equals("") ) {
                       String AG = Config.MasterAgent;
                       findDeviceInfos( AG );
                   } else {

                   }
                   return true;
               } else if (  keyCode == KeyEvent.KEYCODE_BACK ) {
                   finish();
                   return true;
               } else {
               }
               return false;
           }
        });*/
        tvAlltvAllDeivces.setVisibility(View.GONE);
    }

    private TextWatcher textWatcher = new TextWatcher() {

        @Override
        public void afterTextChanged(Editable s) {

        }

        @Override
        public void beforeTextChanged(CharSequence s, int start, int count, int after) {

        }

        @Override
        public void onTextChanged(CharSequence s, int start, int before, int count) {
            String str = finddevice.getText().toString();
            if (str.equals("") || str.equals(null)) {
                tbCancel.setVisibility(View.GONE);
                preferenceUtil.putInt(Config.SELECTSTATUS, -1);
                //背景图片的改变  ----- 后期改为选择器
                tbFind.setVisibility(View.GONE);
                tvAll.setTextColor(Color.WHITE);
                //   tvOnline.setTextColor(Color.BLUE);
                //   tvOffline.setTextColor(Color.BLUE);
                tvAll.setBackgroundResource(R.drawable.blue_bt);
                //    tvOnline.setBackground(null);
                //    tvOffline.setBackground(null);
                //内容的改变
                allAdapter = new DeviceAdapter(Agent_DeviceListActivity.this, allListBeans, R.layout.item_agentdevicelist);
                listview.setAdapter(allAdapter);
            } else {
                preferenceUtil.putInt(Config.SELECTSTATUS, 2);
                //背景图片的改变  ----- 后期改为选择器
                //     tvAll.setTextColor(Color.BLUE);
                //    tvOnline.setTextColor(Color.BLUE);
                //     tvOffline.setTextColor(Color.BLUE);
                //     tvAll.setBackground(null);
                //    tvOnline.setBackground(null);
                //     tvOffline.setBackground(null);
                if ( str.length() == 15 )
                    tbFind.setVisibility(View.VISIBLE);
                else
                    tbFind.setVisibility(View.GONE);
                tbCancel.setVisibility(View.VISIBLE);
                if ( ZhongXunApplication.currentDeviceList.size() > 0 ) {
                    initfindData(finddevice.getText().toString());
                    findAdapter = new DeviceAdapter(Agent_DeviceListActivity.this, findListBeans, R.layout.item_agentdevicelist);
                    listview.setAdapter(findAdapter);
                }
            }
        }
    };

    private void initEvent() {
        listview.setOnItemClickListener(this);
    }

    private void initOtherData() {
        //   onlineListBeans.clear();//清空在线
        //   offlineListBeans.clear();//清空离线
        //    for (int i = 0; i < allListBeans.size(); i++) {
        //        DeviceListBean deviceListBean = allListBeans.get(i);
        //        if (deviceListBean.getFlag().equals("online")) {//线上的数据集合
        //       onlineListBeans.add(deviceListBean);
        //        }

        //       if (deviceListBean.getFlag().equals("offline")) {//离线的数据集合
        //      offlineListBeans.add(deviceListBean);
        //       }
        //    }
    }

    //直接对集合操作
    private void initAllData() {
        //清空集合,再添加  如果一开始集合中有数据的情况下
        allListBeans.clear();

        //第一条显示的string数据(不变的数据)名称+imei
        String deviceDes = null;
        //组成电量+在线状态+速度   如果log为null的情况下直接设置--没有数据
        String deviceStatus = null;

        //左侧图标的id
        int leftId = 0;//初始化
        //右侧图标的id
        int rightId = 0;

        //从全局的list中取出数据放进新的集合中
        //三个集合all online offline
        //左侧读取log(在线/离线---决定图片的颜色)和icon(0/1/2/3---网络/基站/WiFi)的信息--log中不含有in/off的时候显示没有数据
        //上面文字:name(设备名称+[imei])
        //中间文字:bat(电池)+log(离线/在线)+gps(0代表静止)
        //右侧图标:pic(根据类型设置不同的图片)
        int all = 0;
        int on = 0;
        int off = 0;
        user = preferenceUtil.getString(Config.USERNAME);
        word = preferenceUtil.getString(Config.PASSWORD);

        for (int i = 0; i < ZhongXunApplication.currentDeviceList.size(); i++) {//全部的设备信息
            all ++;
            DeviceInfo deviceBean = ZhongXunApplication.currentDeviceList.get(i);
            //先存储所有数据----->>(注意里面的数据有可能为空--null)
            String allName = deviceBean.name;//名称
            String allImei = deviceBean.imei;//imei
            String ver = deviceBean.ver;//电量
            String allBat = deviceBean.bat;//电量
            String log = deviceBean.log;//状态
            String allPic = deviceBean.marker + "";//设备类型对应的pic
            String allIcon = deviceBean.icon + "";//设备在线状态对应的icon
            String allGps = deviceBean.gps;//gps数据,包含速度数据
            String[] splitData = allGps.split(",");
            DeviceListBean deviceListBean = new DeviceListBean();//list列表的item数据
            //组成name+imei
            String model = "";
            try {
                String Sever = preferenceUtil.getString(Config.ServerMODEL);
                if ( !Sever.equals("") && !Sever.equals(null) && !Sever.equals("null")) {
                    model = Sever.substring(Sever.indexOf("M" + deviceBean.device));
                    model = model.substring(model.indexOf("v") + 1);
                    model = model.substring(0, model.indexOf(",") - 1);
                }
            } catch (Exception e) {
            }

            deviceDes = allName + "[" + allImei + "]" ;
            try {
                if ( !ver.equals(model) && !model.equals("") && !ver.equals("") && !ver.equals("0") ) {
                    deviceDes = allName + "[" + allImei + "] " ; //+ UIUtils.getString(R.string.version_set) ;
                    Config.update = true ;
                }
            } catch (Exception e) {
            }

            String status = null;//线上/离线
            //解析log中的数据
            // log time , lat,lng, spd, deg ,sate, source

            Calendar NowDate = Calendar.getInstance(TimeZone.getTimeZone("GMT0"));
            NowDate.add(Calendar.HOUR, -8);
            String logtime = "";
            if ( log.startsWith("IN") || log.startsWith("CH"))
                logtime = log.substring(3);
            else if (log.startsWith("Out") || log.startsWith("OUT") || log.startsWith("SHD") )
                logtime = log.substring(4);
            else if ( log.startsWith("20"))
                logtime = log;

            int mins  = 999999 ;
            if ( !logtime.equals("")) {
                SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.ENGLISH);
                ParsePosition pos = new ParsePosition(0);
                Date strtodate = formatter.parse(logtime, pos);
                mins = MapUtil.minsBetween(strtodate, NowDate.getTime());
            }

            if (log != null && !log.equals("null") && splitData.length >= 5) {//在设备数据不为空的情况下-------设置左侧图标---------
                if ( ( log.startsWith("IN") || log.startsWith("CH") ) && allGps != null && !allGps.equals("null") ) {//在线  根据不同的状态设置图片的颜色(log的信息以IN开头)
                    on ++;
                    deviceListBean.setFlag("online");
                    status = UIUtils.getString(R.string.online);
                    switch (allIcon) {//离线时的图标
                        case "0"://基站
                        case "2":
                            leftId = R.drawable.loc_nlbs;
                            break;
                        case "1"://gps
                            leftId = R.drawable.loc_ngps;
                            break;
                        case "3"://wifi
                            leftId = R.drawable.loc_nwifi;
                            break;
                    }
                } else if ( log.startsWith("Out") || log.startsWith("OUT") || log.startsWith("SHD")) {//离线
                    off ++;
                    deviceListBean.setFlag("offline");
                    String time = "";
                    try {
                        //time = allGps.split(",")[0];
                        time = transform(log.substring(4));
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                    status =  DeviceStatusStringUtils.getOffline() + " " + time;
                    switch (allIcon) {//离线时的图标
                        case "0"://基站
                        case "2":
                            leftId = R.drawable.loc_nlbs_off;
                            break;
                        case "1"://网络
                            leftId = R.drawable.loc_ngps_off;
                            break;
                        case "3"://wifi
                            leftId = R.drawable.loc_nwifi_off;
                    }
                } else {//没有数据
                    deviceListBean.setFlag("empty");
                    deviceStatus = UIUtils.getString(R.string.data_error);
                    leftId = R.drawable.nodata;
                }

                //"gps": time, sate, typ, spd, deg,
                //"gps": "2017-03-06 11:15:58, 3 ,1 ,0 ,0",

                if (allGps != null && !allGps.equals("null") ) {//不为空的情况下提取出速度值,判断时候大于0
                    String speed = null;
                    //String[] splitData = allGps.split(",");
                    //1时间(0) 2纬度  3.经度  4.速度(3)  5.方向
                    //如果速度为0的话显示静止,其他显示具体的速度
                    String deviceSpeed = null;//速度
                    try {
                        deviceSpeed = splitData[3];
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                    String direct = "";
                    try {
                        direct = getDirection(Integer.parseInt(splitData[4]));
                    } catch (Exception e) {
                        e.printStackTrace();
                    }

                    /*if ("0".equals(deviceSpeed)) {//静止
                        speed = UIUtils.getString(R.string.still);//UIUtils.getString(R.string.still)
                    } else */
                    if("0".equals(deviceSpeed)||deviceSpeed==null||"null".equals(deviceSpeed)){
                        speed ="";
                    }else if ( log.startsWith("IN") || log.startsWith("CH") ){//设置数据
                        speed = UIUtils.getString(R.string.speed)+":"+deviceSpeed+UIUtils.getString(R.string.km)+"  "+direct;
                        status = UIUtils.getString(R.string.driving);
                    } else {
                        speed ="";
                    }
                    if(allBat==null||"null".equals(allBat)){
                        // deviceStatus = UIUtils.getString(R.string.bat_error) +" "+ status + " " + speed;
                        deviceStatus = status + " " +speed;
                    }else{
                        deviceStatus = allBat + "% " + " "+status + " " + speed;
                    }
                } else {
                    deviceListBean.setFlag("empty");
                    deviceStatus = UIUtils.getString(R.string.data_error);
                    leftId = R.drawable.nodata;
                }
                //电量为空的情况下

            } else if ( log != null && !log.equals("null") && ( splitData.length < 5 || allGps == null || allGps.equals("null"))) {//log为空的情况下,设备数据为空的情况下   ---左侧图标---
                leftId = R.drawable.nodata;
                if (log.startsWith("IN") || log.startsWith("CH")  ) {//在线  根据不同的状态设置图片的颜色(log的信息以IN开头)
                    deviceListBean.setFlag("online");
                    if(allBat==null||"null".equals(allBat)) {
                        deviceStatus = UIUtils.getString(R.string.online) + " " + UIUtils.getString(R.string.data_error);
                    } else {
                        deviceStatus = allBat + "% " + UIUtils.getString(R.string.online) + " " + UIUtils.getString(R.string.data_error);
                    }
                    //status = UIUtils.getString(R.string.online) + " " + UIUtils.getString(R.string.data_error) ;
                } else if ( log.startsWith("Out") || log.startsWith("OUT") || log.startsWith("SHD")) {//离线
                    deviceListBean.setFlag("offline");
                    if(allBat==null||"null".equals(allBat)) {
                        deviceStatus =  DeviceStatusStringUtils.getOffline() + " " + UIUtils.getString(R.string.data_error);
                    } else {
                        deviceStatus = allBat + "% " +  DeviceStatusStringUtils.getOffline() + " " + UIUtils.getString(R.string.data_error);
                    }
                    //status =  DeviceStatusStringUtils.getOffline() ; //+ " " + time;
                } else {//没有数据
                    deviceStatus = UIUtils.getString(R.string.data_error);
                    deviceListBean.setFlag("empty");
                }
            } else {
                leftId = R.drawable.nodata;
                deviceListBean.setFlag("empty");
                deviceStatus = UIUtils.getString(R.string.data_error);
            }

    /*        switch (allPic) {//右侧小图标    ----右侧小图标----
                case "0": //6001  默认的情况下
                    rightId = R.drawable.m0;
                    break;
                case "1":// 6005C
                    rightId = R.drawable.p1;
                    break;
                case "2":// 6005
                    rightId = R.drawable.m2;
                    break;
                case "3":// pet
                    rightId = R.drawable.m3;
                    break;
                case "4":// baby
                    rightId = R.drawable.m4;
                    break;
                case "5":// car
                    rightId = R.drawable.m5;
                    break;
                case "6":// dog
                    rightId = R.drawable.m6;
                    break;
                case "7":// cat
                    rightId = R.drawable.m7;
                    break;
                case "8"://red
                    rightId = R.drawable.m8;
                    break;
                case "9"://blue
                    rightId = R.drawable.m9;
                    break;
                case "10"://green
                    rightId = R.drawable.m10;
                    break;
                default:
                    break;
            }*/
            //添加进集合中
            deviceListBean.setDevice(deviceDes);
            deviceListBean.setImei(deviceStatus);
            deviceListBean.setLeftIcon(leftId);
            // deviceListBean.setRightIcon(rightId);
            allListBeans.add(deviceListBean);
        }
        tvAll.setText(UIUtils.getString(R.string.all) + "("+ all + ")");
        //    tvOnline.setText(UIUtils.getString(R.string.online) + "("+ on +")");
        //   tvOffline.setText( DeviceStatusStringUtils.getOffline() + "("+ off +")");
    }



    //直接对集合操作
    private void initfindData(String findName) {
        //清空集合,再添加  如果一开始集合中有数据的情况下
        findListBeans.clear();//清空离线
        String deviceDes = null;
        //组成电量+在线状态+速度   如果log为null的情况下直接设置--没有数据
        String deviceStatus = null;
        Boolean chk = false ;
        //左侧图标的id
        int leftId = 0;//初始化
        //右侧图标的id
        int rightId = 0;

        //从全局的list中取出数据放进新的集合中
        //三个集合all online offline
        //左侧读取log(在线/离线---决定图片的颜色)和icon(0/1/2/3---网络/基站/WiFi)的信息--log中不含有in/off的时候显示没有数据
        //上面文字:name(设备名称+[imei])
        //中间文字:bat(电池)+log(离线/在线)+gps(0代表静止)
        //右侧图标:pic(根据类型设置不同的图片)

        for (int i = 0; i < ZhongXunApplication.currentDeviceList.size(); i++) {//全部的设备信息
            // LogUtils.i("sanmysize-------:"+ZhongXunApplication.currentDeviceList.size());
            DeviceInfo deviceBean = ZhongXunApplication.currentDeviceList.get(i);
            //先存储所有数据----->>(注意里面的数据有可能为空--null)
            String allName = deviceBean.name;//名称
            String allImei = deviceBean.imei;//imei

            if ( allName.indexOf(findName) > -1 || allImei.indexOf(findName) > -1 )  {
                chk = true ;
                String allBat = deviceBean.bat;//电量
                String log = deviceBean.log;//状态
                String allPic = deviceBean.marker + "";//设备类型对应的pic
                String allIcon = deviceBean.icon + "";//设备在线状态对应的icon
                String allGps = deviceBean.gps;//gps数据,包含速度数据
                String[] splitData = allGps.split(",");
                DeviceListBean deviceListBean = new DeviceListBean();//list列表的item数据
                //组成name+imei
                deviceDes = allName + "[" + allImei + "]";
                String status = null;//线上/离线
                //解析log中的数据
                Calendar NowDate = Calendar.getInstance(TimeZone.getTimeZone("GMT0"));
                NowDate.add(Calendar.HOUR, -8);
                String logtime = "";
                if (log.startsWith("IN") || log.startsWith("CH")  )
                    logtime = log.substring(3);
                else if ( log.startsWith("Out") || log.startsWith("OUT") || log.startsWith("SHD"))
                    logtime = log.substring(4);
                else if ( log.startsWith("20"))
                    logtime = log;

                int mins  = 999999 ;
                if ( !logtime.equals("")) {
                    SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.ENGLISH);
                    ParsePosition pos = new ParsePosition(0);
                    Date strtodate = formatter.parse(logtime, pos);
                    mins = MapUtil.minsBetween(strtodate, NowDate.getTime());
                }

                if (log != null && !log.equals("null") && splitData.length >= 5 ) {//在设备数据不为空的情况下-------设置左侧图标---------
                    if (log.startsWith("IN") || log.startsWith("CH")  ) {//在线  根据不同的状态设置图片的颜色(log的信息以IN开头)
                        deviceListBean.setFlag("online");
                        status = UIUtils.getString(R.string.online);
                        switch (allIcon) {//离线时的图标
                            case "0"://基站
                            case "2":
                                leftId = R.drawable.loc_nlbs;
                                break;
                            case "1"://gps
                                leftId = R.drawable.loc_ngps;
                                break;
                            case "3"://wifi
                                leftId = R.drawable.loc_nwifi;
                                break;
                        }
                    } else if ( log.startsWith("Out") || log.startsWith("OUT") || log.startsWith("SHD") ) {//离线
                        deviceListBean.setFlag("offline");
                        String time = "";
                        try {
                            time = transform(log.substring(4));
                            //time = allGps.split(",")[0];
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                        status =  DeviceStatusStringUtils.getOffline() + " " + time;
                        switch (allIcon) {//离线时的图标
                            case "0"://基站
                            case "2":
                                leftId = R.drawable.loc_nlbs;
                                break;
                            case "1"://gps
                                leftId = R.drawable.loc_ngps;
                                break;
                            case "3"://wifi
                                leftId = R.drawable.loc_nwifi;
                                break;
                        }
                    } else {//没有数据
                        deviceListBean.setFlag("empty");
                        deviceStatus = UIUtils.getString(R.string.data_error);
                        leftId = R.drawable.nodata;
                        /*switch (allIcon) {//离线时的图标
                            case "0"://基站
                            case "2":
                                leftId = R.drawable.loc_nlbs;
                                break;
                            case "1"://gps
                                leftId = R.drawable.loc_ngps;
                                break;
                            case "3"://wifi
                                leftId = R.drawable.loc_nwifi;
                                break;
                        }*/
                    }

                    String speed = null;
                    //"gps": "2017-03-06 11:15:58,22.575768,113.912766,0,0",
                    if (allGps != null) {//不为空的情况下提取出速度值,判断时候大于0
                        //        String[] splitData = allGps.split(",");
                        //1时间(0) 2纬度  3.经度  4.速度(3)  5.方向
                        //如果速度为0的话显示静止,其他显示具体的速度
                        String deviceSpeed = null;//速度
                        try {
                            deviceSpeed = splitData[3];
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                        String direct = "";
                        try {
                            direct = getDirection(Integer.parseInt(splitData[4]));
                        } catch (Exception e) {
                            e.printStackTrace();
                        }

                    /*if ("0".equals(deviceSpeed)) {//静止
                        speed = UIUtils.getString(R.string.still);//UIUtils.getString(R.string.still)
                    } else */
                        if ("0".equals(deviceSpeed) || deviceSpeed == null || "null".equals(deviceSpeed)) {
                            speed = "";
                        } else {//设置数据
                            speed = UIUtils.getString(R.string.speed) + ":" + deviceSpeed + UIUtils.getString(R.string.km) + "  " + direct;
                            status = UIUtils.getString(R.string.driving);
                        }
                    }
                    //电量为空的情况下
                    if (allBat == null || "null".equals(allBat)) {
                        // deviceStatus = UIUtils.getString(R.string.bat_error) +" "+ status + " " + speed;
                        deviceStatus = status + " " + speed;
                    } else {
                        deviceStatus = allBat + "% " + " " + status + " " + speed;
                    }
                } else {//log为空的情况下,设备数据为空的情况下   ---左侧图标---
                    deviceListBean.setFlag("empty");
                    deviceStatus = UIUtils.getString(R.string.data_error);
                    leftId = R.drawable.nodata;
                }

            /*    switch (allPic) {//右侧小图标    ----右侧小图标----
                    case "0": //6001  默认的情况下
                        rightId = R.drawable.m0;
                        break;
                    case "1":// 6005C
                        rightId = R.drawable.p1;
                        break;
                    case "2":// 6005
                        rightId = R.drawable.m2;
                        break;
                    case "3":// pet
                        rightId = R.drawable.m3;
                        break;
                    case "4":// baby
                        rightId = R.drawable.m4;
                        break;
                    case "5":// car
                        rightId = R.drawable.m5;
                        break;
                    case "6":// dog
                        rightId = R.drawable.m6;
                        break;
                    case "7":// cat
                        rightId = R.drawable.m7;
                        break;
                    case "8"://red
                        rightId = R.drawable.m8;
                        break;
                    case "9"://blue
                        rightId = R.drawable.m9;
                        break;
                    case "10"://green
                        rightId = R.drawable.m10;
                        break;
                    default:
                        break;
                }*/
                //添加进集合中
                deviceListBean.setDevice(deviceDes);
                deviceListBean.setImei(deviceStatus);
                deviceListBean.setLeftIcon(leftId);
                //    deviceListBean.setRightIcon(rightId);
                findListBeans.add(deviceListBean);
            }
        }
        if ( !chk  ) {
            // Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.data_error), Toast.LENGTH_SHORT).show();
        }
    }

    @OnClick({R.id.tvAgent, R.id.tvapw, R.id.tvRefresh, R.id.tvAllDeivces, R.id.tvAll, R.id.tvOnline, R.id.tvOffline, R.id.tbCancel, R.id.tbFind })
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.tvapw:
                new AlertDialog.Builder(Agent_DeviceListActivity.this)
                        //.setMessage(UIUtils.getString(R.string.logout_set))
                        .setTitle(UIUtils.getString(R.string.recover_pwd) + ":11111")
                        .setPositiveButton(UIUtils.getString(R.string.yes),//是
                                new DialogInterface.OnClickListener() {
                                    public void onClick(DialogInterface dialog, int whichButton) {//退出登录
                                        if (isNetworkConnected(Agent_DeviceListActivity.this)) {
                                            mProgressDilog.showProgressDilog(null);
                                            SubmitData(99);
                                        } else
                                            Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.net_no_link), Toast.LENGTH_SHORT).show();
                                    }
                                })
                        .setNegativeButton(Agent_DeviceListActivity.this.getString(R.string.no),
                                new DialogInterface.OnClickListener() {
                                    public void onClick(DialogInterface dialog, int whichButton) {//关闭对话框
                                        dialog.dismiss();
                                    }
                                }).create().show();
                //Intent intent = new Intent(Agent_DeviceListActivity.this, ChangePswActivity.class);
                //startActivityWithAnim(intent);
                break;
            case R.id.tbFind:
                //ToastUtil.show(Agent_DeviceListActivity.this,  "Find:" + finddevice.getText().toString() );
                //log("getDeviceInfos: Agent Find " + finddevice.getText().toString());
                if ( finddevice.getText().toString().length() == 15 ) {
                    if (!isConnected().equals("NULL")) {
                        mProgressDilog.showProgressDilog(null);
                        agentgetDeviceInfos(finddevice.getText().toString(), "", 9);
                    } else
                        Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.net_no_link), Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.nodata), Toast.LENGTH_SHORT).show();
                }
                if (mProgressDilog != null) {
                    mProgressDilog.dissmissProgressDilog();
                }
                break;
            case R.id.tvAgent:
                // Intent intent = new Intent(DeviceListActivity.this, AgentTreeActivity.class);
                //intent.putExtra("state", preferenceUtil.getInt(Config.SELECTSTATUS));
                //startActivityWithAnim(intent);
                finish();
                break;
            case R.id.tvRefresh://刷新
                flag = true;
                if (timer != null) {
                    timer.cancel();
                    timer = null;
                }
                onResume();
                break;
            case R.id.tbCancel:
                finddevice.setText("");
                break;
            case R.id.tvAllDeivces:
                Intent intent = new Intent(Agent_DeviceListActivity.this, DeviceLocationActivity.class);
                intent.putExtra("state", preferenceUtil.getInt(Config.SELECTSTATUS));
                startActivityWithAnim(intent);
                break;
            case R.id.tvAll:
                finddevice.setText("");
                preferenceUtil.putInt(Config.SELECTSTATUS, -1);
                tvAll.setTextColor(Color.WHITE);
                tvAll.setBackgroundResource(R.drawable.blue_bt);
                allAdapter = new DeviceAdapter(Agent_DeviceListActivity.this, allListBeans, R.layout.item_agentdevicelist);
                listview.setAdapter(allAdapter);
                break;
            case R.id.tvOnline://在线设备
                preferenceUtil.putInt(Config.SELECTSTATUS, 1);
                tvAll.setBackground(null);
                tvAll.setTextColor(Color.BLUE);
                break;
            case R.id.tvOffline://离线设备
                preferenceUtil.putInt(Config.SELECTSTATUS, 0);
                tvAll.setBackground(null);
                tvAll.setTextColor(Color.BLUE);
                break;
            /*case R.id.tvDevices:
                preferenceUtil.putInt(Config.SELECTSTATUS, 2);
                tvAll.setBackground(null);
                tvOnline.setBackground(null);
                tvOffline.setBackground(null);
                tvAll.setTextColor(Color.BLUE);
                tvOnline.setTextColor(Color.BLUE);
                tvOffline.setTextColor(Color.BLUE);
                final AlertDialog.Builder builder2 = new AlertDialog.Builder(DeviceListActivity.this);
                View timeSelView = View.inflate(Agent_DeviceListActivity.this, R.layout.dialog_find_device, null);
                Button btnConfirm = (Button) timeSelView.findViewById(R.id.confirm);
                Button btnCancel = (Button) timeSelView.findViewById(R.id.cancel);
                final EditText etName = (EditText) timeSelView.findViewById(R.id.etName);
                etName.setText(postNameStr);
                btnCancel.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {

                        dialog2.dismiss();
                        //记录当前点击的选项,默认为所有的设备
                        preferenceUtil.putInt(Config.SELECTSTATUS, -1);
                        //背景图片的改变  ----- 后期改为选择器
                        tvAll.setTextColor(Color.WHITE);
                        tvOnline.setTextColor(Color.BLUE);
                        tvOffline.setTextColor(Color.BLUE);
                        tvAll.setBackgroundResource(R.drawable.blue_bt);
                        tvOnline.setBackground(null);
                        tvOffline.setBackground(null);
                        //内容的改变
                        allAdapter = new DeviceAdapter(DeviceListActivity.this, allListBeans, R.layout.item_agentdevicelist);
                        listview.setAdapter(allAdapter);
                        return;
                    }
                });
                btnConfirm.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        //提交数据
                        postNameStr = etName.getText().toString().trim();
                        if (TextUtils.isEmpty(postNameStr)) {
                            //记录当前点击的选项,默认为所有的设备
                            preferenceUtil.putInt(Config.SELECTSTATUS, -1);
                            //背景图片的改变  ----- 后期改为选择器
                            tvAll.setTextColor(Color.WHITE);
                            tvOnline.setTextColor(Color.BLUE);
                            tvOffline.setTextColor(Color.BLUE);
                            tvAll.setBackgroundResource(R.drawable.blue_bt);
                            tvOnline.setBackground(null);
                            tvOffline.setBackground(null);
                            //内容的改变
                            allAdapter = new DeviceAdapter(DeviceListActivity.this, allListBeans, R.layout.item_agentdevicelist);
                            listview.setAdapter(allAdapter);
                            return;
                        } else {
                            //内容的改变
                            initfindData(postNameStr);
                            findAdapter = new DeviceAdapter(DeviceListActivity.this, findListBeans, R.layout.item_agentdevicelist);
                            listview.setAdapter(findAdapter);
                        }
                        dialog2.dismiss();
                    }
                });

                builder2.setView(timeSelView);
                dialog2 = builder2.create();
                dialog2.show();

                break;*/
        }
    }

    private void SubmitData(final int typ) {
        String url = null;
        //log("MasterAgent:" + Config.MasterAgent + "\nConfig.PW:" + Config.PW);
       // String al = Config.alevel;
        String[] ag = Config.MasterAgent.split(";");
        if ( !Config.PW.equals("")) {
            url = Config.SERVER_URL + Config.APP + "_agpw.php?login=" + ag[0] + "&typ=" + ag[1] + "&sub=" + ag[2] + "&sl=" + ag[3] + "&npw=111111" + "&tm=" + MapUtil.getzone(this) ;
        }
        //log(url );
        log( getApplicationContext(), url);
        OkHttpUtils
                .get()
                .addHeader("User-Agent", Config.AGENT)
                .url(url)
                .build()
                .connTimeOut(Config.TIMEOUT)
                .readTimeOut(Config.TIMEOUT)
                .writeTimeOut(Config.TIMEOUT)
                .execute(new StringCallback() {
                    @Override
                    public void onError(Call call, Exception e, int id) {
                        ChangeIP(22);
                        Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.net_error), Toast.LENGTH_SHORT).show();
                        if (mProgressDilog != null) {
                            mProgressDilog.dissmissProgressDilog();
                        }
                        return;
                    }

                    @Override
                    public void onResponse(String response, int id) {
                            log(getApplicationContext(), response);
                        //log( response);
                        if ( response.indexOf("Y") > -1 ) {
                            if ( typ == 99) {
                                Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.success_send) + " " + UIUtils.getString(R.string.recover_pwd) +":111111", Toast.LENGTH_SHORT).show();
                            } else {
                                Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.success_send), Toast.LENGTH_SHORT).show();
                            }
                        } else {
                            Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.net_error), Toast.LENGTH_SHORT).show();
                        }
                        if (mProgressDilog != null) {
                            mProgressDilog.dissmissProgressDilog();
                        }
                    }
                });
        if (mProgressDilog != null) {
            mProgressDilog.dissmissProgressDilog();
        }
    }


    //崩溃的时候listview中列表的数据混乱了
    private DeviceInfo device;
    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        //获取当前点击的条目的数据 逻辑有问题
        int selectstatus = preferenceUtil.getInt(Config.SELECTSTATUS);//默认是全部设备列表
        DeviceListBean listBean = null;
        if ( finddevice.getText().toString().equals("")) {
            listBean = allListBeans.get(position);//集合中获取当前点击的对象
        } else {
            listBean = findListBeans.get(position);
        }

        /*switch (selectstatus) {
            case -1://当前选中项为所有设备
                listBean = allListBeans.get(position);//集合中获取当前点击的对象
                break;
            case 1://当前选中项为online
                listBean = onlineListBeans.get(position);
                break;
            case 0://当前选中项为offline
                listBean = offlineListBeans.get(position);
                break;
            case 2://当前选中项为offline
                listBean = findListBeans.get(position);
                break;
            default:
                break;
        }*/
        try {
            //取出IMEI号,保存到全局的配置文件中
            String des = listBean.getDevice();
            ZhongXunApplication.currentName = des.substring(0, des.indexOf("["));
            ZhongXunApplication.currentImei = des.substring(des.indexOf("[") + 1, des.indexOf("]"));//全局的
            //将选中的位置设置到配置文件中
            preferenceUtil.putInt(Config.LVSELPOSI, position);//listView中点击的选项
            ZhongXunApplication.getSelDevice(ZhongXunApplication.currentImei, true);//改变全局的,imei改变的时候,全局的设备信息对应发生改变
            //点击后关闭当前的界面
            preferenceUtil.putString("preimei", ZhongXunApplication.currentImei);
            ZhongXunApplication.initData(ZhongXunApplication.currentImei);
            //点击后关闭当前的界面
            device = ZhongXunApplication.currentDevice;//一开始默认是第一个
            ZhongXunApplication.currentIcon = device.marker;
            if (Config.agent) {
                finish();
            } else {
                if ( device.stop < 0) {
                    Toast.makeText(Agent_DeviceListActivity.this, device.name + " " + UIUtils.getString(R.string.expire_time) + ":" + device.exp + "\n" + UIUtils.getString(R.string.renew), Toast.LENGTH_SHORT).show();
                   // finish();
                    return;
                } else {
                    if ( device.stop < 14) {
                  //      ToastUtil.show(Agent_DeviceListActivity.this,  device.imei + " " + UIUtils.getString(R.string.expire_time) + ":" + device.exp + "\n" + UIUtils.getString(R.string.renew));
                    }
                    finish();
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public class DeviceAdapter extends CommonAdapter<DeviceListBean> {

        public DeviceAdapter(Context context, List<DeviceListBean> datas, int layoutId) {
            super(context, datas, layoutId);
        }

        @Override
        public void convert(ViewHolder holder, DeviceListBean deviceListBean) {
            holder.setBackgroundRes(R.id.netState, deviceListBean.getLeftIcon());
            holder.setText(R.id.tvDevice, deviceListBean.getDevice());
            holder.setText(R.id.tvImei, deviceListBean.getImei());
            holder.setBackgroundRes(R.id.tvIcon, deviceListBean.getRightIcon());
        }
    }

    @Override
    protected void onResume() {
        super.onResume();

        if ( !Config.agent ) {
            user = preferenceUtil.getString(Config.USERNAME);
            word = preferenceUtil.getString(Config.PASSWORD);
            preferenceUtil.putInt(Config.SELECTSTATUS, -1);//每当activity可见的时候设置选中的为all界面

            refreshTime = preferenceUtil.getInt(Config.ZX_REFRESH_TIME);
            if (refreshTime == 0) {
                preferenceUtil.putInt(Config.ZX_REFRESH_TIME, 180);
                refreshTime = 180;
            }
            if (timer == null) {
                timer = new Timer();
            }
            timer.schedule(new TimerTask() {
                @Override
                public void run() {
                    try {
                        if (!isConnected().equals("NULL"))
                            getDeviceInfos(user, word, 3);
                        else
                            Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.net_no_link), Toast.LENGTH_SHORT).show();
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            }, new Date(), refreshTime * 1000);
        }
    }

    //获取当前账号所有设备的信息
    public  void getAgentDeviceInfos(final String AG) {
        String url ;

        if ( AG.indexOf(";") > -1 ) {
            try {
                String[] agData = AG.split(";");
                url = Config.SERVER_URL + Config.APP + "_aglist.php?typ=" + agData[1] + "&level=" + agData[3] + "&agent=" + agData[0] + "&sub=" + agData[2] + "&tm=" +MapUtil.getzone(this) ;

            } catch (Exception e) {
                url = "";
            }
        } else {
            try {
                //String[] agData = AG.split(";");
                String agData = AG.substring(0,AG.indexOf("(")) ; //  AgentDeviceInfos:bbbbbbs(4/4)
                //log("AgentDeviceInfos 1 :" + agData);
                // if ( agData[1].equals("1") || agData[1].equals("2")) {
                url = Config.SERVER_URL + Config.APP + "_aglist.php?typ=" + Config.alevel + "&level=" + Config.alevel + "&agent=" + agData + "&sub=" + agData + "&tm=" +MapUtil.getzone(this) ;
                // }
            } catch (Exception e) {
                url = "";
            }
        }
        //log("get Agent Device List " + url + " ");
        if (!url.equals("")) {
            mProgressDilog.showProgressDilog(null);
    log( getApplicationContext(), url);
        OkHttpUtils
                    .get()
                .url(url)
                .addHeader("User-Agent", Config.AGENT)
                .build()
                    .execute(new StringCallback() {
                        @Override
                        public void onError(Call call, Exception e, int id) {
                            ChangeIP(22);
                            //log("getAgentDeviceInfos onerror");
                            if (neterr == 0) {
                                neterr++;
                                if (mProgressDilog != null) {
                                    mProgressDilog.dissmissProgressDilog();
                                }
                                mRefreshLayout.setRefreshing(false);
                                getAgentDeviceInfos(AG);
                            } else {
                                if (mProgressDilog != null) {
                                    mProgressDilog.dissmissProgressDilog();
                                }
                                mRefreshLayout.setRefreshing(false);
                                Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.net_error), Toast.LENGTH_SHORT).show();
                            }
                            return;
                        }

                        @Override
                        public void onResponse(String response, int id) {
                            log(getApplicationContext(), response);
                            //log(response);
                            neterr = 0;
                            if (response.length() <= 18) {
                                if (mProgressDilog != null) {
                                    mProgressDilog.dissmissProgressDilog();
                                }
                                mRefreshLayout.setRefreshing(false);
                                Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.nodata), Toast.LENGTH_SHORT).show();
                                return;
                            }
                            int locSize = 0;//界面设备个数,默认是0个
                            try {
                                if (response.indexOf("device") > -1) {
                                    JSONArray jsonArray = new JSONArray(response);
                                    String locateData = "";//定位数据
                                    // log("getAgentDeviceInfos length:" + jsonArray.length());
                                    for (int i = 0; i < jsonArray.length(); i++) {
                                        JSONObject jsonObject = jsonArray.getJSONObject(i);//使用单个单个账号登录的时候
                                        String type = jsonObject.getString("device");
                                        String timei = jsonObject.getString("imei");
                                        String tname = jsonObject.getString("name");
                                        int mark = jsonObject.getInt("marker");
                                        if (ZhongXunApplication.currentName == null || ZhongXunApplication.currentName.equals("") || ZhongXunApplication.currentName.equals(null)) {
                                            ZhongXunApplication.currentName = tname;
                                            ZhongXunApplication.currentImei = timei;
                                            ZhongXunApplication.currentIcon = mark;
                                            preferenceUtil.putString("preimei", timei);
                                            ZhongXunApplication.initData(timei);
                                        }
                                        locateData += jsonObject.toString() + ",";
                                        locSize++;
                                    }
                                    //  log("getAgentDeviceInfos locSize:" + locSize);
                                    preferenceUtil.putInt(Config.ZX_LOCSIZE, locSize);
                                    String locSubmit = null;
                                    if (!TextUtils.isEmpty(locateData)) {
                                        locSubmit = "[" + locateData.substring(0, locateData.length() - 1) + "]";//定位保存数据
                                    } else {
                                        locSubmit = "[" + "]";
                                    }

                                    preferenceUtil.putBoolean(Config.ISLOGIN, true);
                                    preferenceUtil.putBoolean(Config.ISREGU, true);
                                    //    log("getAgentDeviceInfos 88" );
                                }

                                JSONArray jsonArray = new JSONArray(response);
                                String locateData = "";//定位数据

                                for (int i = 0; i < jsonArray.length(); i++) {
                                    JSONObject jsonObject = jsonArray.getJSONObject(i);//使用单个单个账号登录的时候
                                    String type = jsonObject.getString("device");
                                    locateData += jsonObject.toString() + ",";
                                    locSize++;
                                    //}
                                }
                                preferenceUtil.putInt(Config.ZX_LOCSIZE, locSize);

                                String locSubmit = null;
                                if (!TextUtils.isEmpty(locateData)) {
                                    locSubmit = "[" + locateData.substring(0, locateData.length() - 1) + "]";//定位保存数据
                                } else {
                                    locSubmit = "[" + "]";
                                }

                                preferenceUtil.putString(Config.ZX_LOCATE_INFO, locSubmit);//定位数据
                                preferenceUtil.putBoolean(Config.ISLOGIN, true);

                                ZhongXunApplication.initData(ZhongXunApplication.currentImei);//原来的不变
                                initAllData();
                                initOtherData();
                                int selectItem = preferenceUtil.getInt(Config.SELECTSTATUS);
                                switch (selectItem) {
                                    case -1://全部
                                        allAdapter.notifyDataSetChanged();//数据源更新
                                        break;
                                    case 1://在线
                                        //     onlineAdapter.notifyDataSetChanged();
                                        break;
                                    case 0://离线
                                        //     offlineAdapter.notifyDataSetChanged();
                                        break;
                                    default:
                                        break;
                                }
                                if (flag) {
                                    Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.refresh_finish), Toast.LENGTH_SHORT).show();
                                    flag = false;
                                }
                                finddevice.setText("");
                                preferenceUtil.putInt(Config.SELECTSTATUS, -1);
                                tvAll.setTextColor(Color.WHITE);
                                tvAll.setBackgroundResource(R.drawable.blue_bt);
                                allAdapter = new DeviceAdapter(Agent_DeviceListActivity.this, allListBeans, R.layout.item_agentdevicelist);
                                listview.setAdapter(allAdapter);
                            } catch (Exception e) {

                            }
                            if (mProgressDilog != null) {
                                mProgressDilog.dissmissProgressDilog();
                            }
                            mRefreshLayout.setRefreshing(false);
                        }
                    });
        } else {
            //log("get Agent Device List1 " + AG );
        }
        //} else {
        //    log("get Agent Device List2 " + AG  );
        //}
    }


    //获取当前账号所有设备的信息
    public  void getDeviceInfos(final String userName, final String passWord, final int no ){
        String url ;
        if ( (System.currentTimeMillis() - Config.logTime) / 1000 < 2 ) {
            return;
        };
        Config.logTime = System.currentTimeMillis();
        int loginMode = preferenceUtil.getInt(Config.ZX_LOGIN_MODE);
        if ( Config.agent ) {
            url = Config.SERVER_URL + Config.APP + "_alist.php?login=" + user.substring(1) + "&pw=" + word  + "&mode=1exp=1"  + "&tm=" +MapUtil.getzone(this) ;
        } else if (loginMode == 0) {//账号登录
            url = Config.SERVER_URL + Config.APP + "_mlist.php?login=" + userName + "&pw=" + passWord + "&exp=1"  + "&tm=" + MapUtil.getzone(this);
        } else if (loginMode == 1) {//imei号登录
            if ( userName.length() == 15) {
                url = Config.SERVER_URL + Config.APP + "_ilist.php?imei=" + userName  + "&pw=" + passWord  + "&exp=1"  + "&tm=" +MapUtil.getzone(this) ;
            } else {
                url = "";
            }
        } else {//其他默认使用的是账号登录
            url = Config.SERVER_URL + Config.APP + "_mlist.php?login=" + userName + "&pw=" + passWord  + "&exp=1"  + "&tm=" +MapUtil.getzone(this) ;
        }
        //log("AgentDevice " + url + " "  + userName + " " + passWord );
        if ( !url.equals("")) {
            mProgressDilog.showProgressDilog(null);
            mRefreshLayout.setRefreshing(false);
    log( getApplicationContext(), url);
        OkHttpUtils
                    .get()
                    .url(url)
                    .addHeader("User-Agent", Config.AGENT)
                    .build()
                    .execute(new StringCallback() {
                        @Override
                        public void onError(Call call, Exception e, int id) {
                            ChangeIP(22);
                            //log("getDeviceInfos onerror"  );
                            if (mProgressDilog != null) {
                                mProgressDilog.dissmissProgressDilog();
                            }
                            mRefreshLayout.setRefreshing(false);
                            return;
                        }

                        @Override
                        public void onResponse(String response, int id) {
                            log(getApplicationContext(), response);
                            //  log("getDeviceInfos:" + response);

                            if (response.length() <= 18) {
                                if (mProgressDilog != null) {
                                    mProgressDilog.dissmissProgressDilog();
                                }

                                Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.nodata), Toast.LENGTH_SHORT).show();
                                mRefreshLayout.setRefreshing(false);
                                return;
                            }
                            int locSize = 0;//界面设备个数,默认是0个
                            try {
                                JSONArray jsonArray = new JSONArray(response);
                                String locateData = "";//定位数据
                                for (int i = 0; i < jsonArray.length(); i++) {
                                    JSONObject jsonObject = jsonArray.getJSONObject(i);//使用单个单个账号登录的时候
                                    String type = jsonObject.getString("device");
                                    locateData += jsonObject.toString() + ",";
                                    locSize++;
                                }
                                preferenceUtil.putInt(Config.ZX_LOCSIZE, locSize);
                                String locSubmit = null;
                                if (!TextUtils.isEmpty(locateData)) {
                                    locSubmit = "[" + locateData.substring(0, locateData.length() - 1) + "]";//定位保存数据
                                } else {
                                    locSubmit = "[" + "]";
                                }
                                preferenceUtil.putString(Config.ZX_LOCATE_INFO, locSubmit);//定位数据
                                if ( Config.VIP.equals("TEST") && finddevice.getText().length() == 15 ) {
                                } else {
                                    //    preferenceUtil.putString(Config.USERNAME, userName);
                                    //    preferenceUtil.putString(Config.PASSWORD, passWord);
                                    //    preferenceUtil.putBoolean(Config.ISLOGIN, true);
                                }
                                ZhongXunApplication.initData(ZhongXunApplication.currentImei);//原来的不变
                                initAllData();//从新调用初始化全局数据的方法----->>所有设备数据的集合发生改变
                                initOtherData();
                                //获取当前选中的选项界面
                                int selectItem = preferenceUtil.getInt(Config.SELECTSTATUS);
                                switch (selectItem) {
                                    case -1://全部
                                        allAdapter.notifyDataSetChanged();//数据源更新
                                        break;
                                    case 1://在线
                                        //      onlineAdapter.notifyDataSetChanged();
                                        break;
                                    case 0://离线
                                        //     offlineAdapter.notifyDataSetChanged();
                                        break;
                                    default:
                                        break;
                                }
                                if (flag) {
                                    Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.refresh_finish), Toast.LENGTH_SHORT).show();
                                    flag = false;
                                }
                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        }
                    });
        }

        if (mProgressDilog != null) {
            mProgressDilog.dissmissProgressDilog();
        }
        mRefreshLayout.setRefreshing(false);
    }

    public  void agentgetDeviceInfos(final String userName, final String passWord, final int no ){
        String url = null;

        int loginMode = preferenceUtil.getInt(Config.ZX_LOGIN_MODE);
        if ( finddevice.getText().length() == 15 ) {
            String AG = Config.MasterAgent;
            String[] agData = AG.split(";");
            //if ( agData[1].equals("1") ) {
                url = Config.SERVER_URL + Config.APP + "_aslist.php?typ=" + agData[1] + "&agent=" + agData[0] +"&imei=" + userName + "&tm=" +MapUtil.getzone(this) ;
            //}
        } else {
        }
        // log("agentgetDeviceInfos " + url + " "  + userName + " " + passWord );
        if ( !url.equals("")) {
            //mProgressDilog.showProgressDilog(null);
    log( getApplicationContext(), url);
        OkHttpUtils
                    .get()
                    .url(url)
                    .addHeader("User-Agent", Config.AGENT)
                    .build()
                    .execute(new StringCallback() {
                        @Override
                        public void onError(Call call, Exception e, int id) {
                            ChangeIP(22);
                            //  log("getDeviceInfos onerror"  );
                            if (mProgressDilog != null) {
                                mProgressDilog.dissmissProgressDilog();
                            }
                            mRefreshLayout.setRefreshing(false);
                            return;
                        }

                        @Override
                        public void onResponse(String response, int id) {
                            log(getApplicationContext(), response);
                            //  log("agentgetDeviceInfos :" + response + " " + response.length());
                            if ( response.length() <= 18 || response.indexOf("result\":\"NULL") > -1 ) {
                                if (mProgressDilog != null) {
                                    mProgressDilog.dissmissProgressDilog();
                                }
                                mRefreshLayout.setRefreshing(false);
                                Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.nodata), Toast.LENGTH_SHORT).show();
                                return;
                            }
                            int locSize = 0;//界面设备个数,默认是0个

                            try {
                                JSONArray jsonArray = new JSONArray(response);
                                String locateData = "";//定位数据
                                for (int i = 0; i < jsonArray.length(); i++) {
                                    JSONObject jsonObject = jsonArray.getJSONObject(i);//使用单个单个账号登录的时候
                                    String type = jsonObject.getString("device");
                                    locateData += jsonObject.toString() + ",";
                                    locSize++;
                                }
                                // log("getDeviceInfos 2:");
                                preferenceUtil.putInt(Config.ZX_LOCSIZE, locSize);
                                String locSubmit = null;
                                if (!TextUtils.isEmpty(locateData)) {
                                    locSubmit = "[" + locateData.substring(0, locateData.length() - 1) + "]";//定位保存数据
                                } else {
                                    locSubmit = "[" + "]";
                                }
                                //log("getDeviceInfos 3:");
                                preferenceUtil.putString(Config.ZX_LOCATE_INFO, locSubmit);//定位数据
                                if ( Config.VIP.equals("TEST") && finddevice.getText().length() == 15 ) {
                                } else {
                                    preferenceUtil.putString(Config.USERNAME, userName);
                                    preferenceUtil.putString(Config.PASSWORD, passWord);
                                    preferenceUtil.putBoolean(Config.ISLOGIN, true);
                                }
                                //log("getDeviceInfos 4:");
                                ZhongXunApplication.initData(ZhongXunApplication.currentImei);//原来的不变

                                if (flag) {
                                    Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.refresh_finish), Toast.LENGTH_SHORT).show();
                                    flag = false;
                                }
                                //finish();
                                mRefreshLayout.setRefreshing(false);
                                finish();
                            } catch (Exception e) {
                                e.printStackTrace();
                            }

                            if (mProgressDilog != null) {
                                mProgressDilog.dissmissProgressDilog();
                            }
                            // log("getDeviceInfos 8:");
                        }
                    });

        }

        if (mProgressDilog != null) {
            mProgressDilog.dissmissProgressDilog();
        }
        mRefreshLayout.setRefreshing(false);
    }

    @Override
    protected void onPause() {
        super.onPause();
        if(timer!=null){
            timer.cancel();
            timer = null;
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if(timer!=null){
            timer.cancel();
            timer = null;
        }
    }

    public class ScreenStatusReceiver extends BroadcastReceiver {
        @Override
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if ("android.intent.action.SCREEN_ON".equals(action)) {//屏幕重新打开的情况下
                if(timer==null){
                    timer = new Timer();
                    timer.schedule(new TimerTask() {
                        @Override
                        public synchronized void run() {
                            try {
                                if ( !isConnected().equals("NULL"))
                                    getDeviceInfos(user, word, 1);
                                else
                                    Toast.makeText(Agent_DeviceListActivity.this, UIUtils.getString(R.string.net_no_link), Toast.LENGTH_SHORT).show();
                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        }
                    }, new Date(), refreshTime * 1000);
                }
            } else if ("android.intent.action.SCREEN_OFF".equals(action)) {//屏幕关闭的情况下
                //锁屏的时候关闭定时器
                if(timer!=null){
                    timer.cancel();
                    timer = null;
                }
            }
        }
    }

    private String isConnected() {
        try {
            ConnectivityManager cm = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
            if (cm != null) {
                @SuppressLint("MissingPermission") NetworkInfo networkInfo = cm.getActiveNetworkInfo();
                if (networkInfo.isConnected()) {
                    if (networkInfo != null
                            && networkInfo.getType() == ConnectivityManager.TYPE_WIFI)
                        return "Wifi";
                    else
                        return "GSM";
                }
            }
        } catch (Exception e) {
        }
        return "NULL";
    }

    private boolean isNetworkConnected(Context context) {
        try {
             if (context != null) {
                ConnectivityManager mConnectivityManager = (ConnectivityManager) context
                        .getSystemService(Context.CONNECTIVITY_SERVICE);
                 @SuppressLint("MissingPermission") NetworkInfo mNetworkInfo = mConnectivityManager.getActiveNetworkInfo();
                 if (mNetworkInfo != null) {
                    return mNetworkInfo.isAvailable();
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return false;
    }
}

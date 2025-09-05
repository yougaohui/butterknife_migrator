package xfkj.fitpro.fragment.base;
import static xfkj.fitpro.application.MyApplication.Logdebug;
import static xfkj.fitpro.application.MyApplication.returnshi;
import static xfkj.fitpro.bluetooth.SendData.getSportKeyDayGet;
import static xfkj.fitpro.utils.DateUtils.getCalendars;
import static xfkj.fitpro.utils.DateUtils.getDate;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.animation.Animation;
import android.view.animation.AnimationSet;
import android.view.animation.AnimationUtils;
import android.view.animation.TranslateAnimation;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.annotation.Nullable;
import androidx.cardview.widget.CardView;
import androidx.core.content.ContextCompat;
import com.blankj.utilcode.util.ActivityUtils;
import com.blankj.utilcode.util.CollectionUtils;
import com.blankj.utilcode.util.LogUtils;
import com.blankj.utilcode.util.TimeUtils;
import com.blankj.utilcode.util.ToastUtils;
import com.blankj.utilcode.util.Utils;
import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineDataSet;
import com.gyf.immersionbar.ImmersionBar;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.sql.Timestamp;
import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import xfkj.fitpro.BuildConfig;
import xfkj.fitpro.R;
import xfkj.fitpro.activity.HealthReportActivity;
import xfkj.fitpro.activity.MeasureActivity;
import xfkj.fitpro.activity.MoreSleepActivity;
import xfkj.fitpro.activity.RankActivity;
import xfkj.fitpro.activity.StepNumberMoreActivity;
import xfkj.fitpro.activity.TempHistoryActivity;
import xfkj.fitpro.activity.ecg.ECGMeasureActivity;
import xfkj.fitpro.activity.habbit.HealthHabbitListActivity;
import xfkj.fitpro.activity.measure.BloodMeasureActivity;
import xfkj.fitpro.activity.measure.HeartMeasureActivity;
import xfkj.fitpro.activity.measure.SpoMeasureActivity;
import xfkj.fitpro.activity.personinfo.PersonalInfoActivity;
import xfkj.fitpro.api.HttpHelper;
import xfkj.fitpro.base.NewBaseFragment;
import xfkj.fitpro.bluetooth.Profile;
import xfkj.fitpro.bluetooth.SDKCmdMannager;
import xfkj.fitpro.db.DBHelper;
import xfkj.fitpro.eum.WatchThemShape;
import xfkj.fitpro.event.ClockDialInfoEvent;
import xfkj.fitpro.event.HideItemEvent;
import xfkj.fitpro.fragment.HomeFragmentNew;
import xfkj.fitpro.model.ECGRecordModel;
import xfkj.fitpro.model.MeasureBloodModel;
import xfkj.fitpro.model.MeasureDetailsModel;
import xfkj.fitpro.model.MeasureHeartModel;
import xfkj.fitpro.model.MeasureSpoModel;
import xfkj.fitpro.model.SleepDetails;
import xfkj.fitpro.model.SleepDetailsModel;
import xfkj.fitpro.model.TempModel;
import xfkj.fitpro.model.sever.body.ClockDialInfoBody;
import xfkj.fitpro.model.sever.reponse.AdvStatus;
import xfkj.fitpro.receiver.LeReceiver;
import xfkj.fitpro.utils.BloodPressureTools;
import xfkj.fitpro.utils.ChannelUtils;
import xfkj.fitpro.utils.ChartViewUtils;
import xfkj.fitpro.utils.CommonUtils;
import xfkj.fitpro.utils.Constant;
import xfkj.fitpro.utils.LanguageUtils;
import xfkj.fitpro.utils.MySPUtils;
import xfkj.fitpro.utils.MyTimeUtils;
import xfkj.fitpro.utils.NumberUtils;
import xfkj.fitpro.utils.SaveKeyValues;
import xfkj.fitpro.utils.SleepUtils;
import xfkj.fitpro.utils.SportCalculator;
import xfkj.fitpro.utils.UnitConvertUtils;
import xfkj.fitpro.utils.WeatherProxy;
import xfkj.fitpro.utils.glide.GlideUitls;
import xfkj.fitpro.view.CircleProgress;
import xfkj.fitpro.view.FangDaFontsTextView;
import xfkj.fitpro.view.HealthScoreRadios;
import xfkj.fitpro.view.MySportView;
/**
 * 新的首页界面
 */
public class HomeBaseFragment extends TabBaseFragment {
    ImageButton mImgbtnRefresh;
    TextView mTvTarget;
    TextView mTvDistance;
    TextView mTvConsume;
    TextView mTvTarget2;
    HealthScoreRadios mHealthScore;
    TextView mTvHealthGrade;
    TextView mTvHeart;
    LineChart mLineChart;
    TextView mTvSleepHour;
    TextView mTvSleepMin;
    CardView mCardviewTemp;
    TextView mTvHeartMax;
    TextView mTvHeartMin;
    TextView mTvSleepDeep;
    TextView mTvSleepSomeone;
    TextView mTvSleepAwake;
    TextView mMDeepSleepBgview;
    TextView mMSomnolenceSleepBgview;
    TextView mMSoberSleepBgview;
    ImageView mImgCup;
    TextView mTvKm;
    TextView mTvTemp;
    TextView mTvTempLabel;
    LineChart mTemplineChart;
    TextView mTvSleepStatus;
    View mCardXinDian;
    TextView mTvLastHrEl;
    TextView mTvStepsToday;
    CircleProgress mCirclePbSteps;
    TextView mTvGrade;
    TextView mTvHeartMax2;
    TextView mTvHeartMin2;
    TextView mTvHeart2;
    TextView mTvBloodStatus;
    TextView mTvBlood;
    TextView mTvSpoStatus;
    TextView mTvSpo;
    ImageView mImgSpoArrow;
    ImageView mImgSpoBar;
    LineChart mLineChart2;
    LineChart mLineChart3;
    ImageView mImgDefHr;
    ImageView mImgDefBld;
    ImageView mImgDefSpo;
    View mCardViewHeart;
    View mCardViewHeart2;
    View mCardViewBlood;
    View mCardViewSpo2;
    View mCardViewSleep;
    public MySportView mSportView;
    public FangDaFontsTextView mTvSteps;
    public TextView mTvDate;
    private View mCardViewWatchTheme;
    private ImageView mImgWatchTheme;
    private int mTargetSteps;//用户的步数
    private Double distance_values;// 路程：米
    private int steps_values;//步数
    private int calory_values;//热量
    private String today;
    private LeReceiver leReceiver;
    private Map dates;
    private ArrayList<HashMap<String, Object>> sleepItem;
    private String t_heart;
    //刷新动画
    private Animation mRotateAnimation;
    private boolean isRunAnim;
    //传值
    private Handler handler = new Handler(new Handler.Callback() {
        @Override
        public boolean handleMessage(Message msg) {
            Map<String, Object> map = (Map<String, Object>) msg.getData().getSerializable("Datas");//接受msg传递过来的参数
            switch (msg.what) {
                case Profile.MsgWhat.what5://步数跟新后会调至这里
                    steps_values = (Integer) map.get("step");//获取计步的步数
                    distance_values = Double.valueOf(map.get("distance").toString());
                    calory_values = (Integer) map.get("calory");
                    if (isRunAnim) {
                        ToastUtils.showShort(R.string.refresh_success);
                        if (mRotateAnimation != null) {
                            mRotateAnimation.cancel();
                            mImgbtnRefresh.clearAnimation();
                        }
                    }
                    //设置显示值
                    updateViewData();
                    break;
                case Profile.MsgWhat.what6://温度返回
                    setTempData((float) map.get("temps"));
                    break;
                case Profile.MsgWhat.what62://血压测量返回
                    showBlood();
                    break;
                case Profile.MsgWhat.what67://血氧测量返回
                    showSpoUI();
                    break;
                case Profile.MsgWhat.what69://血氧测量返回
                    showHeart();
                    break;
                case Profile.MsgWhat.what60://心率测量返回
                case Profile.MsgWhat.what51://步数跟新后会调至这里
                case Profile.MsgWhat.what90://睡眠更新会在这里回调
                case Profile.MsgWhat.what27://心电数据
                    updateViewData();
                    break;
                default:
                    break;
            }
            return false;
        }
    });
    private void setTempData(float temps) {
        setTempValue(temps);
        LineDataSet set = (LineDataSet) mTemplineChart.getData().getDataSetByIndex(0);
        List<Entry> values = set.getValues();
        if (values.size() > 11) {
            values.remove(0);
        }
        Entry entry = new Entry(values.size(), temps);
        values.add(entry);
        int index = 0;
        for (Entry value : values) {
            value.setX(index++);
        }
        set.setValues(values);
        mTemplineChart.getData().notifyDataChanged();
        mTemplineChart.notifyDataSetChanged();
        mTemplineChart.invalidate();
    }
    private void setTempValue(float temps) {
        if (temps < 37.2) {
            mTvTemp.setTextColor(getResources().getColor(R.color.temp_status_color1));
            mTvTempLabel.setTextColor(getResources().getColor(R.color.temp_status_color1));
        } else if (temps < 38) {
            mTvTemp.setTextColor(getResources().getColor(R.color.temp_status_color2));
            mTvTempLabel.setTextColor(getResources().getColor(R.color.temp_status_color2));
        } else if (temps < 39.5) {
            mTvTemp.setTextColor(getResources().getColor(R.color.temp_status_color3));
            mTvTempLabel.setTextColor(getResources().getColor(R.color.temp_status_color3));
        } else {
            mTvTemp.setTextColor(getResources().getColor(R.color.temp_status_color4));
            mTvTempLabel.setTextColor(getResources().getColor(R.color.temp_status_color4));
        }
        String tempStr = (MySPUtils.getTemptUnit() == 0 ? (temps + "") : (UnitConvertUtils.sheshiConvertHuashiFloat(temps) + ""));
        mTvTemp.setText(tempStr);
        mTvTempLabel.setText((MySPUtils.getTemptUnit() == 0 ? getString(R.string.sheshi) : getString(R.string.huashi)));
    }
    public static NewBaseFragment newInstance() {
        return new HomeFragmentNew();
    }
    @Override
    public int getLayoutId() {
        return R.layout.fragment_home_new;
    }
    @Override
    public void initData(Bundle savedInstanceState) {
        initValues();
        leReceiver = new LeReceiver(mContext, handler);
        ChartViewUtils.initHeartRateLineChart(mLineChart);
        ChartViewUtils.initHeartRateLineChart(mLineChart2);
        LineDataSet set = (LineDataSet) mLineChart2.getData().getDataSetByIndex(0);
        set.setCircleRadius(0);
        ChartViewUtils.addBloodSetStyle(set, Color.parseColor("#FFFD4E6B"), Color.parseColor("#FFFFFFFF"), ContextCompat.getDrawable(Utils.getApp(), R.drawable.fade_red));
        set.setMode(LineDataSet.Mode.LINEAR);
        ChartViewUtils.initBloodChart(mLineChart3);
        mLineChart3.getAxisRight().setEnabled(false);
        ChartViewUtils.initTempLineChart(mTemplineChart);
        //动画
        mRotateAnimation = AnimationUtils.loadAnimation(mContext, R.anim.anim_rotate);
        //计算并显示健康得分
        calculateScore();
        refreshData(mImgbtnRefresh);
    }
    @Override
    protected void initViews() {
        super.initViews();
        // 初始化View绑定 - 替换@BindView注解
        mImgbtnRefresh = findViewById(R.id.imgbtn_refresh);
        mTvTarget = findViewById(R.id.tv_target);
        mTvDistance = findViewById(R.id.tv_distance);
        mTvConsume = findViewById(R.id.tv_consume);
        mTvTarget2 = findViewById(R.id.tv_target2);
        mHealthScore = findViewById(R.id.health_score);
        mTvHealthGrade = findViewById(R.id.tv_health_grade);
        mTvHeart = findViewById(R.id.tv_heart);
        mLineChart = findViewById(R.id.lineChart);
        mTvSleepHour = findViewById(R.id.tv_sleep_hour);
        mTvSleepMin = findViewById(R.id.tv_sleep_min);
        mCardviewTemp = findViewById(R.id.cardview_temp);
        mTvHeartMax = findViewById(R.id.tv_heart_max);
        mTvHeartMin = findViewById(R.id.tv_heart_min);
        mTvSleepDeep = findViewById(R.id.tv_sleep_deep);
        mTvSleepSomeone = findViewById(R.id.tv_sleep_someone);
        mTvSleepAwake = findViewById(R.id.tv_sleep_awake);
        mMDeepSleepBgview = findViewById(R.id.m_deep_sleep_bgview);
        mMSomnolenceSleepBgview = findViewById(R.id.m_somnolence_sleep_bgview);
        mMSoberSleepBgview = findViewById(R.id.m_sober_sleep_bgview);
        mImgCup = findViewById(R.id.img_cup);
        mTvKm = findViewById(R.id.tv_km);
        mTvTemp = findViewById(R.id.tv_temp);
        mTvTempLabel = findViewById(R.id.tv_temp_label);
        mTemplineChart = findViewById(R.id.templineChart);
        mTvSleepStatus = findViewById(R.id.tv_sleep_status);
        mCardXinDian = findViewById(R.id.cardview_xindian);
        mTvLastHrEl = findViewById(R.id.tv_last_hr_el);
        mTvStepsToday = findViewById(R.id.tv_steps_today);
        mCirclePbSteps = findViewById(R.id.circle_pb_steps);
        mTvGrade = findViewById(R.id.tv_grade);
        mTvHeartMax2 = findViewById(R.id.tv_heart_max2);
        mTvHeartMin2 = findViewById(R.id.tv_heart_min2);
        mTvHeart2 = findViewById(R.id.tv_heart2);
        mTvBloodStatus = findViewById(R.id.tv_blood_status);
        mTvBlood = findViewById(R.id.tv_blood);
        mTvSpoStatus = findViewById(R.id.tv_spo_status);
        mTvSpo = findViewById(R.id.tv_spo);
        mImgSpoArrow = findViewById(R.id.img_spo_arrow);
        mImgSpoBar = findViewById(R.id.img_spo_bar);
        mLineChart2 = findViewById(R.id.lineChart2);
        mLineChart3 = findViewById(R.id.lineChart3);
        mImgDefHr = findViewById(R.id.img_def_hr);
        mImgDefBld = findViewById(R.id.img_def_bld);
        mImgDefSpo = findViewById(R.id.img_def_spo);
        mCardViewHeart = findViewById(R.id.cardview_heart);
        mCardViewHeart2 = findViewById(R.id.cardview_heart2);
        mCardViewBlood = findViewById(R.id.cardview_blood);
        mCardViewSpo2 = findViewById(R.id.cardview_spo);
        mCardViewSleep = findViewById(R.id.cardview_sleep);
    }
    private TextView getTvMjAddHomeCalory() {
        return (TextView) findViewById(R.id.tv_mj_add_home_calory);
    }
    private void showOrHideTempView() {
        if (MySPUtils.isSupportTemp()) {
            mCardviewTemp.setVisibility(View.VISIBLE);
            List<TempModel> temps = DBHelper.getLastNTempModelOfDesc(10);
            if (!CollectionUtils.isEmpty(temps)) {
                //顺序翻转一下，图表示自左向右一次递增
                List<TempModel> reversalTemps = new ArrayList<>();
                for (int i = temps.size() - 1; i >= 0; i--) {
                    reversalTemps.add(temps.get(i));
                }
                ChartViewUtils.setTempLineChartData(mTemplineChart, reversalTemps);
                //显示当前温度
                setTempValue(temps.get(0).getTmp() / 10f);
            } else {
                ChartViewUtils.setTempLineChartData(mTemplineChart, temps);
            }
        } else {
            mCardviewTemp.setVisibility(View.GONE);
        }
    }
    /**
     * 计算健康得分
     */
    private void calculateScore() {
        int score = SportCalculator.calculateHealthScore();
        String level = mHealthScore.showScore(score);
        mTvHealthGrade.setText(String.valueOf(score));
        mTvGrade.setText(level);
    }
    @Override
    public void initListener() {
        mRotateAnimation.setAnimationListener(new Animation.AnimationListener() {
            @Override
            public void onAnimationStart(Animation animation) {
                isRunAnim = true;
            }
            @Override
            public void onAnimationEnd(Animation animation) {
                isRunAnim = false;
            }
            @Override
            public void onAnimationRepeat(Animation animation) {
            }
        });
        if (null != mCardViewWatchTheme) {
            mCardViewWatchTheme.setOnClickListener(v -> enterWatchThemePage());
        }
        
        // 新增的点击事件监听器
        // 初始化点击事件 - 替换@OnClick注解
        mImgbtnRefresh.setOnClickListener(v -> onMImgbtnRefreshClicked(v));

        findViewById(R.id.ll_steps).setOnClickListener(v -> onMCardviewSportClicked());

        mTvTarget.setOnClickListener(v -> onMCardviewSportClicked());

        mCirclePbSteps.setOnClickListener(v -> onMCardviewSportClicked());

        findViewById(R.id.rl_top_container).setOnClickListener(v -> onMCardviewSportClicked());

        findViewById(R.id.cardview_health).setOnClickListener(v -> onMCardviewHealthClicked());

        mCardViewHeart.setOnClickListener(v -> onMCardviewHeartClicked());

        mCardViewHeart2.setOnClickListener(v -> onMCardviewHeart2Clicked());

        mCardViewBlood.setOnClickListener(v -> onMCardviewBloodClicked());

        mCardViewSpo2.setOnClickListener(v -> onMCardviewSpoClicked());

        mCardViewSleep.setOnClickListener(v -> onMCardviewSleepClicked());

        mCardXinDian.setOnClickListener(v -> onMCardviewXinDianClicked());

        findViewById(R.id.cardview_health_habit).setOnClickListener(v -> onMCardviewHealthHabitClicked());

        mImgCup.setOnClickListener(v -> onMRlRankHeaderClicked());

        findViewById(R.id.rl_target_container).setOnClickListener(v -> onMRlTargetContainerClicked());

        mTemplineChart.setOnClickListener(v -> onViewClicked(v));

        mCardviewTemp.setOnClickListener(v -> onViewClicked(v));

    }
    /**
     * 初始化相关的属性
     */
    private void initValues() {
        sleepItem = new ArrayList<>();
        dates = getDate();
        today = dates.get("date").toString();
        String today1 = dates.get("month").toString() + dates.get("day").toString();
        distance_values = Double.valueOf(SaveKeyValues.getStringValues("distance_values" + today1, "0"));
        calory_values = SaveKeyValues.getIntValues("calory_values" + today1, 0);
        steps_values = SaveKeyValues.getIntValues("steps_values" + today1, 0);
        t_heart = "0";
        Date nowDate = TimeUtils.getNowDate();
        String dateStr = TimeUtils.date2String(nowDate, new SimpleDateFormat("MM.dd", Locale.ENGLISH)) + " " + MyTimeUtils.getWeekByDate2(nowDate);
        if (isCreate()) {
            if (null != mTvDate) {
                mTvDate.setText(dateStr);
            }
        }
    }
    private void updateViewData() {
        //重新获取
        initValues();
        LogUtils.i("==================>>updateViewData!");
        mTargetSteps = SaveKeyValues.getIntValues("step", 5000);//用户的目标步数
        showStepProgressView();
        mCirclePbSteps.setMaxProgress(mTargetSteps);
        mCirclePbSteps.setProgress(steps_values);
        mTvStepsToday.setText(steps_values + "");
        mTvTarget.setText(getString(R.string.trget_txt) + ":" + mTargetSteps + "");
        mTvTarget2.setText(steps_values >= mTargetSteps ? R.string.completed : R.string.incomplete);
        //距离
        String distance = NumberUtils.keepPrecision(UnitConvertUtils.getConvertDist(distance_values), 1, BigDecimal.ROUND_FLOOR);
        if (null == getMjAddHomeDistance()) {
            mTvDistance.setText(distance);
        } else {
            String distanceStr = getString(R.string.distance) + " " + distance + " " + getString(R.string.km);
            getMjAddHomeDistance().setText(distanceStr);
        }
        mTvKm.setText(UnitConvertUtils.getConvertMileUnite());
        //卡路里
        if (null == getTvMjAddHomeCalory()) {
            mTvConsume.setText(calory_values + "");
        } else {
            String caloryStr = getString(R.string.consume) + " " + calory_values + " " + getString(R.string.kcary_txt);
            getTvMjAddHomeCalory().setText(caloryStr);
        }
        if (null != mTvSteps) {
            mTvSteps.setText(String.valueOf(steps_values));
        }
        Logdebug(TAG, "updateViewData" + today + "---distance_values---" + distance_values + "---calory_values---" + calory_values + "---steps_values---" + steps_values);
        setData();
        calculateScore();
        showOrHideView();
    }
    private void showStepProgressView() {
        if (null != mSportView) {
            mSportView.setProgress(steps_values);
            mSportView.setMaxProgress(mTargetSteps);
        }
    }
    private TextView getMjAddHomeDistance() {
        return (TextView) findViewById(R.id.tv_mj_add_home_distance);
    }
    //设置数据
    private void setData() {
        LogUtils.i("==================>>setData!");
        SleepData();
        int max = 0, min = 0;
        List<MeasureDetailsModel> measureDetails = DBHelper.getMeasureDetailsByDateDes(7);
        if (measureDetails != null && measureDetails.size() > 0) {
            //显示最近一条数据
            MeasureDetailsModel lastMeasure = measureDetails.get(0);//最近一条测量值
            t_heart = String.valueOf(lastMeasure.getHeart());
            mTvHeart.setText(t_heart);
            //显示最大最小心率值
            max = measureDetails.get(0).getHeart();
            min = measureDetails.get(0).getHeart();
            for (MeasureDetailsModel measureDetail : measureDetails) {
                max = (max > measureDetail.getHeart() ? max : measureDetail.getHeart());
                min = (min < measureDetail.getHeart() ? min : measureDetail.getHeart());
            }
            //显示图表
            List<Entry> values = new ArrayList<>();
            for (int i = 0; i < 7; i++) {
                int heart = 0;
                if (i < CollectionUtils.size(measureDetails)) {
                    MeasureDetailsModel data = measureDetails.get(i);
                    heart = data.getHeart();
                }
                values.add(new Entry(i, heart));
            }
            ChartViewUtils.setHeartRateLineChartData(mLineChart, values);
        }
        mTvHeartMax.setText(getString(R.string.heart_max, max + ""));
        mTvHeartMin.setText(getString(R.string.heart_min, min + ""));
    }
    private void showHeart() {
        int max = 0, min = 0;
        //单个心率血压血氧显示
        //心率
        List<MeasureHeartModel> hearts = DBHelper.getMeasureOfHeart(7);
        if (!CollectionUtils.isEmpty(hearts)) {
            //显示最大最小心率值
            max = hearts.get(0).getHeart();
            min = hearts.get(0).getHeart();
            MeasureHeartModel newestHeart = hearts.get(0);
            for (MeasureHeartModel heart : hearts) {
                max = (max > heart.getHeart() ? max : heart.getHeart());
                min = (min < heart.getHeart() ? min : heart.getHeart());
            }
            mTvHeart2.setText(String.valueOf(newestHeart.getHeart()));
            mImgDefHr.setVisibility(View.INVISIBLE);
            mLineChart2.setVisibility(View.VISIBLE);
        } else {
            mImgDefHr.setVisibility(View.VISIBLE);
            mLineChart2.setVisibility(View.INVISIBLE);
        }
        //显示图表
        List<Entry> values = new ArrayList<>();
        for (int i = 0; i < 7; i++) {
            int heart = 0;
            if (i < CollectionUtils.size(hearts)) {
                MeasureHeartModel data = hearts.get(i);
                heart = data.getHeart();
            }
            values.add(new Entry(i, heart));
        }
        ChartViewUtils.setHeartRateLineChartData(mLineChart2, values);
        mTvHeartMax2.setText(getString(R.string.heart_max, max + ""));
        mTvHeartMin2.setText(getString(R.string.heart_min, min + ""));
    }
    private void showBlood() {
        //血压
        MeasureBloodModel blood = DBHelper.getLastMeasureBlood();
        if (blood != null) {
            mTvBlood.setText(blood.getHBlood() + "/" + blood.getLBlood());
            int level = BloodPressureTools.getBloodPresureLevel(blood);
            if (level == 1) {
                mTvBloodStatus.setText(R.string._status_normal);
            } else {
                mTvBloodStatus.setText(R.string._status_not_normal);
            }
        } else {
            mTvBloodStatus.setText(R.string._status_none);
        }
        List<Entry> hBloods = new ArrayList<>();
        List<Entry> lBloods = new ArrayList<>();
        List<MeasureBloodModel> bloods = DBHelper.getMeasureOfBlood(7);
        if (!CollectionUtils.isEmpty(bloods)) {
            List<MeasureBloodModel> as = new ArrayList<>();
            for (int i = bloods.size() - 1; i >= 0; i--) {
                MeasureBloodModel lblood = bloods.get(i);
                as.add(lblood);
            }
            for (int i = 0; i < as.size(); i++) {
                MeasureBloodModel lblood = as.get(i);
                Entry entryH = new Entry(i, lblood.getHBlood());
                Entry entryL = new Entry(i, lblood.getLBlood());
                entryH.setData(lblood.getDate());
                entryL.setData(lblood.getDate());
                hBloods.add(entryH);
                lBloods.add(entryL);
            }
            mImgDefBld.setVisibility(View.INVISIBLE);
            mLineChart3.setVisibility(View.VISIBLE);
        } else {
            Entry hBloodEntity = new Entry(-1, 0);
            Entry lBloodEntity = new Entry(-1, 0);
            hBloods.add(hBloodEntity);
            lBloods.add(lBloodEntity);
            mImgDefBld.setVisibility(View.VISIBLE);
            mLineChart3.setVisibility(View.INVISIBLE);
        }
        ChartViewUtils.setBloodChartData(mLineChart3, hBloods, lBloods);
    }
    private void showSpoUI() {
        if (mCardViewSpo2.getVisibility() != View.VISIBLE) {
            Log.e(TAG, "mCardViewSpo not visity");
            return;
        }
        MeasureSpoModel spoModel = DBHelper.getLastMeasureSpo();
        int spo;
        if (spoModel != null) {
            mImgSpoArrow.setVisibility(View.VISIBLE);
            mImgSpoBar.setVisibility(View.VISIBLE);
            mImgDefSpo.setVisibility(View.INVISIBLE);
            spo = spoModel.getSpo();
            mTvSpo.setText(spoModel.getSpo() + "%");
            if (spo < 90) {
                mTvSpoStatus.setText(R.string._status_lower);
            } else if (spo > 90 && spo < 94) {
                mTvSpoStatus.setText(R.string._status_little_lower);
            } else {
                mTvSpoStatus.setText(R.string._status_normal);
            }
            spo = spo < 70 ? 70 : spo;
            spo = spo > 100 ? 100 : spo;
            int spoW = mImgSpoBar.getWidth();
            int spoA = mImgSpoArrow.getWidth();
            float offset;
            if (spo > 97) {
                offset = ((30 - (100 - 98)) / 30f) * spoW;
            } else {
                offset = ((30 - (100 - spo)) / 30f) * spoW;
            }
            AnimationSet animationSet = new AnimationSet(true);
            TranslateAnimation translateAnimation = new TranslateAnimation(Animation.RELATIVE_TO_SELF, 0.0f, Animation.ABSOLUTE, offset, Animation.RELATIVE_TO_SELF, 0.0f, Animation.RELATIVE_TO_SELF, 0f);
            translateAnimation.setDuration(2000);
            animationSet.setFillAfter(true);
            animationSet.addAnimation(translateAnimation);
            mImgSpoArrow.startAnimation(animationSet);
            if (spoW == 0 || spoA == 0) {
                mHandler.postDelayed(() -> {
                    if (isCreate()) {
                        showSpoUI();
                    }
                }, 500);
            }
        } else {
            mTvSpoStatus.setText(R.string._status_none);
            mImgSpoArrow.setVisibility(View.INVISIBLE);
            mImgSpoBar.setVisibility(View.INVISIBLE);
            mImgDefSpo.setVisibility(View.VISIBLE);
        }
    }
    private void SleepData() {
        LogUtils.i("初始化睡眠数据!");
        sleepItem.clear();
        String year = dates.get("year").toString();
        String month = dates.get("month").toString();
        Integer day = Integer.valueOf(dates.get("day").toString());
        String sday3 = day < 10 ? "0" + day : day + "";
        String endStr = year + "-" + month + "-" + sday3 + " 12:00:00";
        Calendar ca = getCalendars(1);
        int month1 = ca.get(Calendar.MONTH) + 1;
        day = ca.get(Calendar.DAY_OF_MONTH);
        month = month1 < 10 ? "0" + month1 : month1 + "";
        String sday2 = day < 10 ? "0" + day : day + "";
        String starStr = year + "-" + month + "-" + sday2 + " 18:00:00";
        Timestamp stime = Timestamp.valueOf(starStr);
        Timestamp etime = Timestamp.valueOf(endStr);
        float deep_sleep_times = 0, somnolence_times = 0, wakeup_times = 0;
        long start_sleep_data = 0;
        int pstype = 0;
        List<SleepDetailsModel> sleepDatas = DBHelper.getSleepDetailsDatasByDateAsc(stime.getTime(), etime.getTime());
        LogUtils.i("查看睡眠数据数据库:cursor count:" + sleepDatas == null ? "0" : sleepDatas.size());
        if (sleepDatas != null && sleepDatas.size() >= 6) {
            List<SleepDetailsModel> effectsSleepDatas = new ArrayList<>();//有效的睡眠数据
            for (SleepDetailsModel sleepData : sleepDatas) {
                //过滤不合法的时间
                if (MyTimeUtils.isOutSleepTime(sleepData.getDate())) {
                    Log.i(TAG, "不合法的睡眠时间");
                    continue;
                }
                effectsSleepDatas.add(sleepData);
                LogUtils.i("debug睡眠 Num:1");
                HashMap<String, Object> sleeps = new HashMap<>();
                int stype = sleepData.getSleepType();
                long longDate = sleepData.getDate().getTime();
                if (start_sleep_data == 0) {
                    start_sleep_data = longDate;
                    pstype = stype;
                }
                LogUtils.i("debug睡眠 Num:2");
                float t = longDate - start_sleep_data;
                if (pstype == 2) {//2到1是或者2到3都是浅睡时间
                    sleeps.put("stype", 2);
                    somnolence_times += t;
                    Log.i(TAG, "====================>>tt;" + t / 1000 / 60 + ";stype:" + 2);
                } else if (pstype == 1) {//1到2是深睡时间
                    sleeps.put("stype", 1);
                    deep_sleep_times += t;
                    Log.i(TAG, "====================>>tt;" + t / 1000 / 60 + ";stype:" + 1);
                } else if (pstype == 3) {//3到2是清醒时间
                    sleeps.put("stype", 3);
                    wakeup_times += t;
                    Log.i(TAG, "====================>>tt;" + t / 1000 / 60 + ";stype:" + 3);
                }
                LogUtils.i("debug睡眠 Num:3");
                sleeps.put("stime", t);
                start_sleep_data = longDate;
                pstype = stype;
                if (t > 0) {
                    sleepItem.add(sleeps);
                }
                LogUtils.i("debug睡眠 Num:4");
            }
            deep_sleep_times = deep_sleep_times / 1000 / 60;
            somnolence_times = somnolence_times / 1000 / 60;
            wakeup_times = wakeup_times / 1000 / 60;
            LogUtils.i("debug睡眠 Num:5");
            //超过6个的有效睡眠数据才显示
            if (effectsSleepDatas != null && effectsSleepDatas.size() >= 6) {
                String beginDate = TimeUtils.date2String(effectsSleepDatas.get(0).getDate(), new SimpleDateFormat("HHmm", Locale.ENGLISH));
                String endDate = TimeUtils.date2String(effectsSleepDatas.get(effectsSleepDatas.size() - 1).getDate(), new SimpleDateFormat("HHmm", Locale.ENGLISH));
                showView(deep_sleep_times, somnolence_times, wakeup_times, beginDate, endDate);
            }
        }
    }
    public void showView(float deep_sleep_times, float somnolence_times, float wakeup_times, String asSleep, String wakeup) {
        Log.i(TAG, "deep_sleep_times:" + deep_sleep_times + ";somnolence_times:" + somnolence_times + ";wakeup_times:" + wakeup_times);
        if (deep_sleep_times > 60 * 4) {//深睡时间大于浅睡时间不展示当天睡眠
            deep_sleep_times = somnolence_times = wakeup_times = 0;
            sleepItem.clear();
        } else {
            try {
                SleepDetails details = new SleepDetails();
                details.setAsSleep(Integer.valueOf(asSleep));
                details.setWakeup(Integer.valueOf(wakeup));
                details.setDeepDur((int) deep_sleep_times);
                details.setLightDur((int) somnolence_times);
                details.setWakeDur((int) wakeup_times);
                HttpHelper.getInstance().saveSleepTime(details);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        float total = deep_sleep_times + somnolence_times + wakeup_times;
        int hour = (int) Math.floor(total / 60);
        int minute = (int) total % 60;
        mTvSleepHour.setText(hour + "");
        mTvSleepMin.setText(returnshi(minute));
        int deepPercent = deep_sleep_times <= 0 ? 0 : (Math.round(deep_sleep_times / total * 100));
        int someoneSpTime = somnolence_times <= 0 ? 0 : (Math.round(somnolence_times / total * 100));
        int wakeTimes = 100 - deepPercent - someoneSpTime;
        wakeTimes = wakeTimes < 0 ? 0 : wakeTimes;
        wakeTimes = wakeTimes > 100 ? 100 : wakeTimes;
        if (total == 0) {
            wakeTimes = 0;
        }
        mTvSleepDeep.setText(getString(R.string.deep_sleep_txt) + deepPercent + "%");
        mTvSleepSomeone.setText(getString(R.string.somnolence_sleep_txt) + someoneSpTime + "%");
        mTvSleepAwake.setText(getString(R.string.sober_txt) + wakeTimes + "%");
        mTvSleepStatus.setText(getString(R.string.sleep_stutas, SleepUtils.getSleepQuality(total, deep_sleep_times)));
        LinearLayout.LayoutParams layoutParams1 = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.MATCH_PARENT);
        layoutParams1.weight = Math.abs(deep_sleep_times);
        mMDeepSleepBgview.setLayoutParams(layoutParams1);
        LinearLayout.LayoutParams layoutParams2 = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.MATCH_PARENT);
        layoutParams2.weight = Math.abs(somnolence_times);
        mMSomnolenceSleepBgview.setLayoutParams(layoutParams2);
        LinearLayout.LayoutParams layoutParams3 = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.MATCH_PARENT);
        layoutParams3.weight = Math.abs(wakeup_times);
        mMSoberSleepBgview.setLayoutParams(layoutParams3);
    }
    /**
     * 计算并格式化doubles数值，保留两位有效数字
     *
     * @param doubles
     * @return 返回当前路程
     */
    private String formatDouble(Double doubles) {
        DecimalFormat df1 = new DecimalFormat("#.#");
        df1.setRoundingMode(RoundingMode.FLOOR);
        return df1.format(doubles);
    }
    @Override
    public void onResume() {
        super.onResume();
        updateViewData();
        if (leReceiver != null) leReceiver.registerLeReceiver();
        showOrHideView();
        showHeart();
        showBlood();
        showSpoUI();
        //自动刷新
        SDKCmdMannager.getTotalSportData();
        checkShowClockDial();
    }
    @Override
    public void onPause() {
        super.onPause();
        if (leReceiver != null) leReceiver.unregisterLeReceiver();
    }
    @Override
    public void onDestroyView() {
        super.onDestroyView();
        this.isRunAnim = false;
    }
    @Override
    public void onHiddenChanged(boolean hidden) {
        super.onHiddenChanged(hidden);
        if (!hidden) {
            updateViewData();
        }
    }
    public void onMImgbtnRefreshClicked(View view) {
        refreshData(view);
    }
    /**
     * 刷新数据
     *
     * @param view
     */
    private void refreshData(View view) {
        updateViewData();
        if (Constant.BleState == 1) {
            if (!isRunAnim) {
                view.startAnimation(mRotateAnimation);
                Constant.mService.commandPoolWrite(getSportKeyDayGet(true), "app请求获取天总结实时数据");//app请求获取天总结实时数据
                //请求天气
                WeatherProxy.getWeatherFromNetwork(false);
            }
        } else {
            ToastUtils.showShort(R.string.unconnected);
        }
    }
    public void onMCardviewSportClicked() {
        ActivityUtils.startActivity(StepNumberMoreActivity.class);
    }
    public void onMCardviewHealthClicked() {
        ActivityUtils.startActivity(HealthReportActivity.class);
    }
    public void onMCardviewHeartClicked() {
        ActivityUtils.startActivity(MeasureActivity.class);
    }
    public void onMCardviewHeart2Clicked() {
        ActivityUtils.startActivity(HeartMeasureActivity.class);
    }
    public void onMCardviewBloodClicked() {
        ActivityUtils.startActivity(BloodMeasureActivity.class);
    }
    public void onMCardviewSpoClicked() {
        ActivityUtils.startActivity(SpoMeasureActivity.class);
    }
    public void onMCardviewSleepClicked() {
        ActivityUtils.startActivity(MoreSleepActivity.class);
    }
    public void onMCardviewXinDianClicked() {
        Intent intent = new Intent(getActivity(), ECGMeasureActivity.class);
        intent.putExtra("isTouch", true);
        intent.putExtra("status", -1);
        ActivityUtils.startActivity(intent);
    }
    public void onMCardviewHealthHabitClicked() {
        if (CommonUtils.isLoginTips()) {
            ActivityUtils.startActivity(HealthHabbitListActivity.class);
        }
    }
    public void onMRlRankHeaderClicked() {
        if (CommonUtils.isLoginTips()) {
            ActivityUtils.startActivity(RankActivity.class);
        }
    }
    public void onMRlTargetContainerClicked() {
        Intent intent = new Intent(mContext, PersonalInfoActivity.class);
        intent.putExtra("isShowTargetStep", true);
        startActivity(intent);
    }
    @Override
    public void onMessageEvent(Object event) {
        super.onMessageEvent(event);
        if (event instanceof HideItemEvent) {
            showOrHideView();
        } else if (event instanceof ClockDialInfoEvent) {
            showWatchThemeImg();
        }
    }
    private void showOrHideHeartBloodSpo() {
        if (ChannelUtils.isHiWatchPlusLayout()) {
            byte[] hbs = MySPUtils.isSupportHeartRateBloodSPO();
            mCardViewHeart2.setVisibility(hbs[0] == 1 ? View.GONE : View.VISIBLE);
            mCardViewBlood.setVisibility(hbs[1] == 1 ? View.GONE : View.VISIBLE);
            mCardViewSpo2.setVisibility(hbs[2] == 1 ? View.GONE : View.VISIBLE);
        } else {
            showOrHideHeartRateView();
        }
    }
    public void onViewClicked(View view) {
        ActivityUtils.startActivity(TempHistoryActivity.class);
    }
    @Nullable
    @Override
    public View onCreateView(LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = super.onCreateView(inflater, container, savedInstanceState);
        createView(view);
        return view;
    }
    protected void createView(View view) {
    }
    private void showOrHideView() {
        showOrHideHrEl();
        showOrHideTempView();
        showOrHideHeartBloodSpo();
        showOrHideSleepView();
    }
    //隐藏或显示睡眠入口
    private void showOrHideSleepView() {
        boolean isHideSleepCardView = !MySPUtils.isSurpportSleep();
        mCardViewSleep.setVisibility(isHideSleepCardView ? View.GONE : View.VISIBLE);
    }
    //隐藏或者显示三合一心率血压血氧入口
    private void showOrHideHeartRateView() {
        boolean isHideHeartCardView = !MySPUtils.isSurpportHeart() && !MySPUtils.isSupportBlood() && !MySPUtils.isSupportSpo();
        mCardViewHeart.setVisibility(isHideHeartCardView ? View.GONE : View.VISIBLE);
    }
    private void showOrHideHrEl() {
        if (MySPUtils.isSupportHREL()) {
            mCardXinDian.setVisibility(View.VISIBLE);
            ECGRecordModel hrel = DBHelper.getTodayRecentData();
            if (hrel != null) {
                mTvLastHrEl.setText(" " + hrel.getHeartRate() + " ");
            }
        } else {
            mCardXinDian.setVisibility(View.GONE);
        }
    }
    @Override
    public void initImmersionBar() {
        ImmersionBar.with(this).keyboardEnable(true).fitsSystemWindows(getResources().getBoolean(R.bool.home_menu_1_fitwindow)).statusBarDarkFont(getResources().getBoolean(R.bool.home_menu_1_dart_dark), 0.2f).barColor(R.color.bar_color_home_1).navigationBarEnable(getResources().getBoolean(R.bool.navigationBarEnable)).init();
    }
    /**
     * 检测是否支持表盘功能
     */
    @Override
    protected void checkShowClockDial() {
        if (mCardViewWatchTheme != null) {
            if (MySPUtils.isSupportClockDialSettings() || BuildConfig.DEBUG) {
                mCardViewWatchTheme.setVisibility(View.VISIBLE);
            } else {
                mCardViewWatchTheme.setVisibility(View.GONE);
            }
            showWatchThemeImg();
        }
    }
    private void showWatchThemeImg() {
        if (null == mImgWatchTheme) {
            return;
        }
        String url = "";
        AdvStatus status = DBHelper.getAdvStatus();
        if (status != null) {
            ClockDialInfoBody watchThemeInfo = getWatchThemeInfo();
            if (watchThemeInfo != null) {
                //判断是否是圆形表盘
                if (watchThemeInfo.getScreenType() == WatchThemShape.CIRCLE.getType()) {
                    //判断语言
                    if (LanguageUtils.isZh()) {
                        url = status.getHome_dial_cn_1();
                    } else {
                        url = status.getHome_dial_en_1();
                    }
                } else {
                    //判断语言
                    if (LanguageUtils.isZh()) {
                        url = status.getHome_dial_cn_0();
                    } else {
                        url = status.getHome_dial_en_0();
                    }
                }
            }
        }
        GlideUitls.loadLocal(mContext, url, R.mipmap.home_dial_en_0, mImgWatchTheme);
    }
}